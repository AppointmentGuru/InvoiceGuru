import requests
from django.conf import settings
from .guru import get_headers
from django import template

DEFAULT_INVOICEE_TEMPLATE = """{{first_name}} {{last_name}}{% if email %}
email: {{email}}{% endif %}{% if cell_phone %}
contact: {{phone_number}}{% endif %}
{{home_address}}
"""

DEFAULT_MEDICAL_AID_TEMPLATE = """{{name}}. {{scheme}}
#{{number}}.
Patient:
{{patient_first_name}} {{patient_last_name}}
ID: {{patient_id_number}}}{% if is_dependent %}
Main member:
{{member_first_name}} {{member_last_name}}
ID: {{member_id_number}}
{% endif %}
"""

class InvoiceBuilder:
    '''
from invoice.invoicebuilder import InvoiceBuilder
from invoice.models import Invoice
inv = Invoice.objects.order_by('?').first()
inv.appointments = [a.get('id') for a in inv.context.get('appointments')]
print(InvoiceBuilder().build_context(inv))


# enrichment process:
from invoice.invoicebuilder import InvoiceBuilder
from invoice.models import Invoice
builder = InvoiceBuilder(invoice)
builder.enrich(with_save=True) # expand context
builder.set_customer_info_from_context() # set customer info + medical aid info if possible
builder.apply_settings() # unless various fields are set, set them from settings
builder.profit()
    '''

    def __init__(self, invoice):
        self.invoice = invoice

    def __render_templated(self, content, data):

        tmplt = template.Template(content)
        context = template.Context(data)
        return tmplt.render(context).strip()

    def apply_settings(self, invoice, settings, with_save=False):

        settings = self.invoice.settings
        settings_to_apply = [
            ('billing_address', 'billing_address'),
            ('integrate_medical_aid', 'integrate_medical_aid'),
        ]
        if settings is None:
            from invoice.models import InvoiceSettings
            settings = InvoiceSettings()
            settings.practitioner_id = self.invoice.practitioner_id
            settings.save()

        for setting_field, invoice_field in settings_to_apply:
            setting_value = getattr(settings, setting_field, None)
            invoice_value = getattr(self.invoice, invoice_field, None)

            setting_exists = setting_value is not None

            if setting_exists and invoice_value is None:
                setattr(self.invoice, invoice_field, setting_value)

        if with_save:
            self.invoice.save()

    def update_invoice_from_context(self):
        if self.invoice.context is not None:
            medicalaid_info = self.invoice.context.get('medicalaid_info')
            if medicalaid_info is not None:
                self.invoice.medicalaid_details = medicalaid_info.strip()

            invoicee_details = self.invoice.context.get("customer_info")
            if invoicee_details is not None:
                self.invoice.invoicee_details = invoicee_details.strip()

            if self.invoice.title is None:
                self.invoice.title = self.invoice.invoice_number

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

        # appointments = self.get_appointments_from_legacy_context()
        appointments = self.get_appointments(
                        self.invoice.practitioner_id,
                        self.invoice.appointments)

        practitioner, raw_practitioner = self.get_practitioner(self.invoice.practitioner_id)

        context.update({
            "client": self.get_client(self.invoice.practitioner_id, self.invoice.customer_id),
            "practitioner": practitioner,
            "appointments": appointments,
            "record": self.get_record(self.invoice.practitioner_id, self.invoice.customer_id)
        })
        self.update_invoice_from_context()

        self.invoice.context = context
        self.apply_settings(self.invoice, self.invoice.settings)

        if save_context:
            self.invoice.save()

        return context

    def get_formatted_invoicee_details(self, client):
        template_string = None
        if self.invoice.settings is not None:
            template_string = self.invoice.settings.customer_info
        if template_string is None:
            template_string = DEFAULT_INVOICEE_TEMPLATE
        return self.__render_templated(template_string, client)

    def get_formatted_medical_aid_details(self, medical_aid):
        template_string = DEFAULT_MEDICAL_AID_TEMPLATE
        return self.__render_templated(template_string, medical_aid)

    def set_customer_info_from_context(self, with_save=False):
        '''
        from values in context, set invoicee_details and medicalaid_details
        '''
        record = self.invoice.context.get('record', {})
        client = record.get('patient', None) or self.invoice.context.get('client', None)
        aid = record.get('medical_aid')

        if client is not None:
            if client.get('phone_number') is None:
                client.upate({
                    "phone_number": client.get("cell_phone")
                })
            self.invoice.invoicee_details = self.get_formatted_invoicee_details(client)

        if aid is not None:
            self.invoice.medicalaid_details = self.get_formatted_medical_aid_details(aid)

        if with_save:
            self.invoice.save()
        return self.invoice

    def reduce(self, obj, fields_to_keep):
        new_obj = {}
        if obj is None or not isinstance(obj, dict):
            return new_obj

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
        client = self.clean_client(data.get("client"))
        practitioner = self.fierce_clean_practitioner(data.get("practitioner"))
        data.update({
            "client": client,
            "practitioner": practitioner
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
