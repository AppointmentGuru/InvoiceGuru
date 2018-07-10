import requests
from django.conf import settings
from .guru import get_headers
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

    def populate_appointments_from_context(self):
        appointments = self.context.get('appointments',[])
        self.invoice.appointments = [appt.get('id') for appt in appointments]
        self.invoice.save()

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
        context.update({
            "client": self.get_client(self.invoice.practitioner_id, self.invoice.customer_id),
            "practitioner": self.get_practitioner(self.invoice.practitioner_id),
            "appointments": self.get_appointments(self.invoice.practitioner_id, self.invoice.appointments),
            "record": self.get_record(self.invoice.practitioner_id, self.invoice.customer_id)
        })
        if save_context:
            self.invoice.context = context
            self.invoice.save()
        return context

    def reduce(self, obj, fields_to_keep):

        new_obj = {}
        for field in fields_to_keep:
            new_obj[field] = obj.get(field)
        return new_obj

    def clean_practitioner(self, practitioner):
        profile = practitioner.get("profile", {})
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'email']
        profile_fields = ['practice_name','practice_number','logo_picture','currency','profession']

        user = self.reduce(practitioner, fields)
        profile = self.reduce(profile, profile_fields)
        user.update(profile)
        return user

    def get_client(self, practitioner_id, customer_id):
        base = settings.APPOINTMENTGURU_API
        path = '/api/users/'
        url = "{}{}{}/".format(base, path, customer_id)
        headers = get_headers(customer_id)
        return requests.get(url, headers=headers).json()

    def get_record(self, practitioner_id, customer_id):

        headers = get_headers(practitioner_id)
        url = '{}/records/{}/'.format(settings.MEDICALAIDGURU_API, customer_id)
        record_request = requests.get(url, headers=headers)
        return record_request.json()

    def get_practitioner(self, practitioner_id):
        base = settings.APPOINTMENTGURU_API
        path = '/api/v2/practitioner/me/'
        url = '{}{}'.format(base, path)
        result = requests.get(url, headers=get_headers(practitioner_id))

        practitioner = result.json().get("results", [])[0]
        return self.clean_practitioner(practitioner)

    def get_appointments(self, practitioner_id, appointment_ids):

        headers = get_headers(practitioner_id)
        appointments = []

        for appointment_id in appointment_ids:
            url = '{}/api/appointments/{}/'.format(settings.APPOINTMENTGURU_API, appointment_id)
            result = requests.get(url, headers=headers)
            if result.status_code == 200:
                data = result.json()
                del data['process']
                data.update({
                    "practitioner": self.clean_practitioner(data.get("practitioner"))
                })
                appointments.append(data)
        return appointments
