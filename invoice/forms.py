from django import forms
from django.conf import settings
from django.template import Template, Context
from .models import  ProofOfPayment, Invoice
from .tasks import submit_to_medical_aid
from .guru import get_headers

import requests

def medicalaids():
    base = settings.MEDICALAIDGURU_API
    path = '/medicalaid/'
    url = '{}{}'.format(base,path)
    data = requests.get(url).json().get('results', [])
    return data

class ProofOfPaymentForm(forms.ModelForm):
    class Meta:
        model = ProofOfPayment
        fields = ['document']

class QuickInvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = [
            'practitioner_id',
            'customer_id',
            'appointments',
            'title',
            'template',
            'date',
            'due_date',
            'invoice_period_from',
            'invoice_period_to',
            'template'
        ]

class MedicalAidSubmissionForm(forms.Form):

    customer_email = forms.EmailField(
        required=True,
        label='Your email address',
        help_text='Medical aid responses will be sent to this email address'
    )
    claims_email = forms.EmailField(
        required=True,
        label='Medical aid claims email address',
        help_text='We\'ll send your invoice to this address'
    )

    @staticmethod
    def get_medicalaid(invoice):
        id = invoice.context.get('record', {}).get('medical_aid', {}).get('medicalaid')
        if id is None: return None
        aids = medicalaids()
        for aid in aids:
            if str(aid.get("id")) == str(id):
                return (aid, aids)

    def save(self, invoice):
        # submit to medical aid
        customer_email = self.cleaned_data.get('customer_email')
        claims_email = self.cleaned_data.get('claims_email')

        data = {
            "to_email": claims_email,
            "from_email": customer_email,
            "invoice_id": invoice.id
        }
        return submit_to_medical_aid(data)


class UpdateInvoiceDetailsForm(forms.Form):

    # medical aid info:
    medicalaid = forms.CharField(required=True)
    name = forms.CharField(required=False, widget=forms.HiddenInput())
    scheme = forms.CharField(required=False)
    number = forms.CharField(required=False)
    # name = forms.CharField(required=True)

    # patient details
    patient_first_name = forms.CharField(required=True)
    patient_last_name = forms.CharField(required=True)
    patient_id_number = forms.CharField(required=True)

    is_dependent = forms.BooleanField(required=False, label='Patient is a dependant')

    member_first_name = forms.CharField(required=False)
    member_last_name = forms.CharField(required=False)
    member_id_number = forms.CharField(required=False)

    def get_medicalaids(self):
        return medicalaids()

    @classmethod
    def from_customer(cls, customer_id, practitioner_id):
        headers = get_headers(customer_id)
        base = settings.MEDICALAIDGURU_API
        path = '/records/{}/?customer_id={}&practitioner_id={}'.format(
            customer_id,
            customer_id,
            practitioner_id
        )
        url = "{}{}".format(base, path)
        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            initial_data = result.json().get("medical_aid")
            return cls(initial=initial_data)

        return cls()

    def save_medicalaid(self, customer_id, medicalaid):
        headers = get_headers(customer_id)
        base = settings.MEDICALAIDGURU_API
        path = '/records/{}/'.format(customer_id)

        record = {
            "medical_aid": medicalaid
        }
        url = '{}{}'.format(base, path)
        print (url)
        print (record)
        print (headers)
        return requests.patch(url, json=record, headers=headers)

    def save(self, invoice, commit = True):
        data = self.cleaned_data
        result = self.save_medicalaid(invoice.customer_id, data)
        print (result)
        print (result.content)

        formatted_medical_aid = """{{name}}
{% if scheme %}{{scheme}}{% endif %}
#: {{number}}
Patient details:
{{patient_first_name}} {{patient_last_name}}
{% if patient_id_number %}ID Number: {{patient_id_number}}{% endif %}
{% if not is_dependent %}✓ Patient is main member{% else %}
Main member details:
{{member_first_name}} {{member_last_name}}
{% if member_id_number %}ID Number: {{member_id_number}}{% endif %}{% endif %}"""
        context = Context(data)
        template = Template(formatted_medical_aid)
        invoice.context.update({
            "medicalaid_info": template.render(context)
        })
        invoice.save()
        return invoice

class InvoiceConstructionForm(forms.Form):

    practitioner_id = forms.CharField(required=True)
    appointment_ids = forms.CharField(required=True)
    client_id = forms.CharField(required=True)
    default_context = forms.CharField(required=True)

    def save(self, commit = True):
        clean_data = self.cleaned_data
        practitioner_id = clean_data.get('practitioner_id')
        appointments = clean_data.get('appointment_ids').split(',')
        client_id = clean_data.get('client_id')

        practitioner, appointments, medical_record = fetch_data(
            practitioner_id, appointment_ids, client_id)
        context = to_context(
                    practitioner,
                    appointments,
                    medical_record,
                    default_context=default_context,
                    format_times = False,
                    format_codes = False)
        data = {
            "context": context,
        }
        if commit == True:
            invoice = Invoice()
            invoice.context = context
            invoice.practitioner_id = practitioner_id
            invoice.customer_id = client_id
            extra_fields = ['practitioner_id', 'customer_id',
                            'title', 'invoice_period_from', 'invoice_period_to',
                            'sender_email', 'date', 'due_date']
            for field in extra_fields:
                value = context.get(field, None)
                if value is not None:
                    setattr(invoice, field, value)

            invoice.save()
            data['id'] = invoice.id
            data['password'] = invoice.password
            return Invoice
        return context

