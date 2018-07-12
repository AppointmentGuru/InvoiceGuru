from rest_framework import serializers
from .models import Invoice, InvoiceSettings, Payment

INVOICE_COMMON_FIELDS = [
    'id',
    'practitioner_id',
    'customer_id',
    'title',
    'status',
    'password',
    'invoice_period_from',
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


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = INVOICE_COMMON_FIELDS + ['context']
        ordering = ('date', 'created',)