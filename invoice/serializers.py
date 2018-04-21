from rest_framework import serializers
from .models import Invoice, InvoiceSettings

class InvoiceListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'practitioner_id', 'customer_id', 'title', 'status',
                  'password', 'invoice_period_from', 'object_ids',
                  'invoice_period_to', 'invoice_amount', 'amount_paid', 'date', 'due_date',]
        ordering = ('date', 'created',)

class InvoiceSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvoiceSettings
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'practitioner_id', 'customer_id', 'title', 'status',
                  'context', 'template', 'password', 'invoice_period_from',
                  'invoice_period_to', 'currency', 'invoice_amount', 'amount_paid', 'date', 'due_date',]
        ordering = ('date', 'created',)