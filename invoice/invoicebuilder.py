import requests
from django.conf import settings
from django import template
from api.api import get_micro

DEFAULT_INVOICEE_TEMPLATE = """{{first_name}} {{last_name}}{% if email %}
email: {{email}}{% endif %}{% if phone_number %}
contact: {{phone_number}}{% endif %}
{{billing_address}}
"""

DEFAULT_MEDICAL_AID_TEMPLATE = """{{name|default:""}}. {{scheme|default:""}}{% if number %}
#{{number}}.{% endif %}
Patient:
{{patient_first_name}} {{patient_last_name}}
ID: {{patient_id_number}}}{% if is_dependent %}
Main member:
{{member_first_name}} {{member_last_name}}
ID: {{member_id_number}}
{% endif %}
"""

def truthy(val):
    return bool(val)


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

    def apply_settings(self, invoice, settings=None, with_save=False):

        if settings is None:
            settings = self.invoice.settings
        settings_to_apply = [
            ('billing_address', 'billing_address'),
            ('integrate_medical_aid', 'integrate_medical_aid'),
            ('banking_details', 'banking_details'),
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
            if setting_exists and not truthy(invoice_value):
                setattr(self.invoice, invoice_field, setting_value)

        if with_save:
            self.invoice.save()

    def set_object_ids(self):
        pass

    def enrich_resource(self, service, resource, id, field, cleaner = None):
        practitioner_id = self.invoice.practitioner_id
        m = get_micro(service, practitioner_id)
        result, data, ok = m.get(resource, id)
        if cleaner is not None:
            data = getattr(self, cleaner)(data)
        setattr(self.invoice, field, data)

    def enrich(self, with_save=False):

        # appointments = self.get_appointments_from_legacy_context()
        appointments = self.get_appointments(
                        self.invoice.practitioner_id,
                        self.invoice.appointments)

        self.enrich_resource("appointmentguru", "practitioner", self.invoice.practitioner_id, "practitioner_data", "clean_practitioner")
        self.enrich_resource("appointmentguru", "user", self.invoice.customer_id, "client_data", "clean_client")
        self.enrich_resource("medicalaidguru", "record", self.invoice.customer_id, "record_data")
        self.invoice.appointment_data = appointments

        self.set_customer_info()

        self.apply_settings(self.invoice, self.invoice.settings)
        self.set_customer_info()

        if with_save:
            self.invoice.save()

        return self.invoice

    def get_formatted_invoicee_details(self, client):
        template_string = None
        if self.invoice.settings is not None:
            template_string = self.invoice.settings.customer_info
        if not truthy(template_string):
            template_string = DEFAULT_INVOICEE_TEMPLATE
        return self.__render_templated(template_string, client)

    def get_formatted_medical_aid_details(self, medical_aid):
        template_string = DEFAULT_MEDICAL_AID_TEMPLATE
        return self.__render_templated(template_string, medical_aid)

    def set_customer_info(self, with_save=False):
        '''
        from values in context, set invoicee_details and medicalaid_details
        prefer details from record, roll back to user if need be
        '''
        record = self.invoice.record_data
        client = record.get('patient', None) or self.invoice.client_data
        # client = record.get('patient', None) or inv.client_data
        aid = record.get('medical_aid')

        if client is not None:
            if not truthy(client.get('phone_number')):
                client.update({
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

    def get_appointments(self, practitioner_id, appointment_ids):

        appointments = []
        for appointment_id in appointment_ids:
            m = get_micro("appointmentguru", self.invoice.practitioner_id)
            result, data, ok = m.get("appointment", appointment_id)
            if ok:
                cleaned = self.clean_appointment(data)
                appointments.append(cleaned)
            else:
                print("{}: Appt #{}: {}".format(practitioner_id, appointment_id, result.status_code))
        return appointments
