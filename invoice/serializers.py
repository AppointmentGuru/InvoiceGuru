from rest_framework import serializers
from .models import Invoice

class InvoiceListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'practitioner_id', 'customer_id', 'title', 'status',
                  'password', 'invoice_period_from', 'object_ids',
                  'invoice_period_to', 'invoice_amount', 'amount_paid', 'date', 'due_date',]
        ordering = ('date', 'created',)

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'practitioner_id', 'customer_id', 'title', 'status',
                  'context', 'template', 'password', 'invoice_period_from',
                  'invoice_period_to', 'currency', 'invoice_amount', 'amount_paid', 'date', 'due_date',]
        ordering = ('date', 'created',)