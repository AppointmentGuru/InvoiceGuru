from django import forms

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

