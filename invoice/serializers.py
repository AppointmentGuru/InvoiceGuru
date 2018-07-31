from rest_framework import serializers
from .models import Invoice, InvoiceSettings, Transaction

INVOICE_COMMON_FIELDS = [
    'id',
    'practitioner_id',
    'customer_id',
    'title',
    'status',
    'password',
    'invoice_period_from',
    'template',
    'object_ids',
    'appointments',
    'invoice_period_to',
    'currency',
    'invoice_amount',
    'amount_paid',
    'amount_due',
    'date',
    'due_date',
    'integrate_medical_aid',
    'show_snapcode_on_invoice',
    'get_snapscan_url',
    'get_snapscan_qr',
    'get_download_url',
    'get_view_url'
]

class InvoiceListViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = INVOICE_COMMON_FIELDS
        ordering = ('date', 'created',)

class InvoiceSettingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvoiceSettings
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Transaction
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = INVOICE_COMMON_FIELDS + ['context']
        ordering = ('date', 'created',)