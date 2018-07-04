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

    def clean_invoice(self, invoice):
        return self.build_context(
            invoice.customer_id,
            invoice.practitioner_id,
            None,
            invoice.appointment_ids
        )

    def build_context(self, invoice):

        context = {}
        context.update({
            "client": self.get_client(invoice.practitioner_id, invoice.customer_id),
            "practitioner": self.get_practitioner(invoice.practitioner_id),
            "appointments": self.get_appointments(invoice.practitioner_id, invoice.appointments),
            "record": self.get_record(invoice.practitioner_id, invoice.customer_id)
        })
        return context

    def reduce(self, obj, fields_to_keep):

        new_obj = {}
        for field in fields_to_keep:
            new_obj[field] = obj.get(field)
        return new_obj

    def clean_practitioner(self, practitioner):
        profile = practitioner.get("profile")
        fields = ['first_name', 'last_name', 'phone_number', 'email']
        profile_fields = ['practice_name','practice_number','logo_picture','currency','profession']

        user = self.reduce(practitioner, fields)
        profile = self.reduce(profile, profile_fields)
        user.update(profile)
        return user

    def get_client(self, practitioner_id, client_id):
        base = settings.APPOINTMENTGURU_API
        path = '/api/v2/practitioner/clients/'
        url = "{}{}{}/".format(base, path, client_id)
        headers = get_headers(practitioner_id)
        return requests.get(url, headers=headers).json()

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

    def get_record(self, practitioner_id, client_id):

        headers = get_headers(practitioner_id)
        url = '{}/records/{}'.format(settings.MEDICALAIDGURU_API, client_id)
        record_request = requests.get(url, headers=headers)
        return record_request.json()