import requests
from django.conf import settings
from .guru import get_headers
from invoice.models import InvoiceSettings

class InvoiceBuilder:
    '''
from invoice.invoicebuilder import InvoiceBuilder
from invoice.models import Invoice
inv = Invoice.objects.order_by('?').first()
inv.appointments = [a.get('id') for a in inv.context.get('appointments')]
print(InvoiceBuilder().build_context(inv))
    '''

    def __init__(self, invoice):
        self.invoice = invoice

    def get_billing_address(self, practitioner):
        address = practitioner\
                    .get("profile", {})\
                    .get("services", [{}])[0]\
                    .get("address", {})

        return """{}
{}
""".format(address.get('name'), address.get('address'))

    def update_settings(self, practitioner):
        settings = self.invoice.settings
        if settings is None:
            settings = InvoiceSettings()
            settings.practitioner_id = self.invoice.practitioner_id

        if settings.billing_address is None:
            settings.billing_address = self.get_billing_address(practitioner)

        if settings.integrate_medical_aid is None:
            settings.integrate_medical_aid = self.invoice.context.get('medicalaid_info') is not None
        settings.save()

    def update_invoice_from_context(self):
        if self.invoice.context is not None:
            medicalaid_info = self.invoice.context.get('medicalaid_info')
            if medicalaid_info is not None:
                self.invoice.medicalaid_details = medicalaid_info.strip()

            invoicee_details = self.invoice.context.get("customer_info")
            if invoicee_details is not None:
                self.invoice.invoicee_details = invoicee_details.strip()

    def populate_appointments_from_context(self):
        appointments = self.invoice.context.get('appointments',[])
        self.invoice.appointments = [appt.get('id') for appt in appointments]
        self.invoice.save()

    def set_object_ids(self):
        pass

    def enrich(self, save_context=False):
        '''
        Invoice()
        invoice.customer_id =
        invoice.practitioner_id =
        invoice.appointments = []
        invoice.save()

        context = InvoiceBuilder(invoice).enrich(save_context=True)
        '''

        context = {}

        appointments = self.get_appointments_from_legacy_context()
        if appointments is None:
            appointments = self.get_appointments(self.invoice.practitioner_id, self.invoice.appointments)

        practitioner, raw_practitioner = self.get_practitioner(self.invoice.practitioner_id)

        self.update_settings(raw_practitioner)

        context.update({
            "client": self.get_client(self.invoice.practitioner_id, self.invoice.customer_id),
            "practitioner": practitioner,
            "appointments": appointments,
            "record": self.get_record(self.invoice.practitioner_id, self.invoice.customer_id)
        })
        self.update_invoice_from_context()
        if save_context:
            self.invoice.context = context
            self.invoice.save()

        self.update_settings(raw_practitioner)
        return context

    def reduce(self, obj, fields_to_keep):
        new_obj = {}
        if obj is None: return new_obj
                    
        for field in fields_to_keep:
            new_obj[field] = obj.get(field)
        return new_obj

    def clean_practitioner(self, practitioner):
        profile = practitioner.get("profile", {})
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email']
        profile_fields = ['practice_name','practice_number','logo_picture','currency','profession', 'banking_details', 'sub_domain']

        if practitioner is not None:
            user = self.reduce(practitioner, fields)
        if profile is not None:
            profile = self.reduce(profile, profile_fields)
            user.update(profile)
        return user

    def clean_client(self, client):
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email']
        return self.reduce(client, fields)

    def fierce_clean_practitioner(self, practitioner):
        profile = practitioner.get("profile", {})
        fields = ['id', 'first_name', 'last_name']
        profile_fields = ['practice_name','practice_number','profession']

        user = self.reduce(practitioner, fields)
        profile = self.reduce(profile, profile_fields)
        user.update(profile)
        return user

    def clean_appointment(self, appointment):
        fields = [
            'id', 'client', 'practitioner', 'codes', 'start_time', 'end_time',
            'currency', 'price', 'amount_paid', 'title', 'invoice_title',
            'full_name', 'invoice_description', 'editable_by_client',
            'invoiceable', 'product'
        ]
        data = self.reduce(appointment, fields)
        data.get('client')
        data.update({
            "client": self.clean_client(data.get("client")),
            "practitioner": self.fierce_clean_practitioner(data.get("practitioner"))
        })
        return data

    def get_client(self, practitioner_id, customer_id):
        base = settings.APPOINTMENTGURU_API
        path = '/api/users/'
        url = "{}{}{}/".format(base, path, customer_id)
        headers = get_headers(customer_id)
        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            return result.json()
        return {}

    def get_record(self, practitioner_id, customer_id):

        headers = get_headers(practitioner_id)
        url = '{}/records/{}/?customer_id={}&practitioner_id={}'.format(
            settings.MEDICALAIDGURU_API,
            customer_id,
            customer_id,
            practitioner_id
        )
        record_request = requests.get(url, headers=headers)
        if record_request.status_code == 200:
            return record_request.json()
        else:
            print(record_request.content)
            print(url)
            print(headers)

    def get_practitioner(self, practitioner_id):
        base = settings.APPOINTMENTGURU_API
        path = '/api/practitioners/{}/'.format(practitioner_id)
        url = '{}{}'.format(base, path)
        result = requests.get(url)

        if result.status_code == 200:
            return (
                self.clean_practitioner(result.json()),
                result.json()
            )
        return ({}, {})

    def get_appointments_from_legacy_context(self):
        # return none if no context already exists on here
        CONTEXT_IS_NONE = self.invoice.context is None
        NO_APPOINTMENTS = self.invoice.context.get('appointments', None) is None
        if CONTEXT_IS_NONE or NO_APPOINTMENTS: return None

        appointments = []
        for appointment in self.invoice.context.get('appointments', []):
            cleaned_appointment = self.clean_appointment(appointment)
            appointments.append(cleaned_appointment)
        return appointments

    def get_appointments(self, practitioner_id, appointment_ids):

        headers = get_headers(practitioner_id)
        appointments = []

        for appointment_id in appointment_ids:
            url = '{}/api/appointments/{}/'.format(
                settings.APPOINTMENTGURU_API,
                appointment_id
            )
            result = requests.get(url, headers=headers)
            if result.status_code == 200:
                data = self.clean_appointment(result.json())
                appointments.append(data)
            else:
                print("{}: Appt #{}: {}".format(practitioner_id, appointment_id, result.status_code))
        return appointments
