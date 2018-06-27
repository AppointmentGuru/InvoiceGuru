from django import forms
from django.template import Template, Context
from .models import  ProofOfPayment

class ProofOfPaymentForm(forms.ModelForm):
    class Meta:
        model = ProofOfPayment
        fields = ['document']

class UpdateInvoiceDetailsForm(forms.Form):

    # medical aid info:
    medical_aid = forms.CharField(required=True)
    medical_aid_scheme = forms.CharField(required=False)
    medical_aid_number = forms.CharField(required=True)

    # patient details
    patient_first_name = forms.CharField(required=True)
    patient_last_name = forms.CharField(required=True)
    patient_id_number = forms.CharField(required=True)

    is_main_member = forms.BooleanField(required=False, label='I am the main member', initial=True)

    main_member_first_name = forms.CharField(required=False)
    main_member_last_name = forms.CharField(required=False)
    main_member_id_number = forms.CharField(required=False)

    def save(self, invoice, commit = True):
        data = self.cleaned_data
        print(data)

        formatted_medical_aid = """Medical Aid: {{medical_aid}}
Scheme: {{medical_aid_scheme}}
Medical Aid #: {{medical_aid_number}}
Patient details:
{{patient_first_name}} {{patient_last_name}}
ID Number: {{medical_aid_number}}
{% if is_main_member %}Patient is main member
{% else %}
Main member details:
{{main_member_first_name}} {{main_member_last_name}}
ID Number: {{main_member_id_number}}{% endif %}"""
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
        import ipdb;ipdb.set_trace()
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

