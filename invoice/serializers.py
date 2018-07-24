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


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = '__all__'

TRANSACTION_TYPES = [
    ('invoice', 'Invoice'),
    ('payment', 'Payment'),
]

class TransactionSerializer(serializers.Serializer):

    invoice_id = serializers.CharField(max_length=36, allow_blank = True)
    payment_id = serializers.CharField(max_length=36, allow_blank = True)
    customer_id = serializers.CharField(max_length=36, allow_blank = True)

    type = serializers.ChoiceField(choices=TRANSACTION_TYPES)
    customer_name = serializers.CharField(max_length=255)
    invoice_number = serializers.CharField(max_length=20)
    description = serializers.CharField(allow_blank = True)
    date = serializers.DateTimeField()
    charge = serializers.DecimalField(decimal_places=2, default=0, max_digits=8, coerce_to_string=True)
    credit = serializers.DecimalField(decimal_places=2, default=0, max_digits=8, coerce_to_string=True)

    @classmethod
    def from_invoice(cls, invoice):
        data = {
            "type": "invoice",
            "invoice_id": invoice.id,
            "customer_id": invoice.customer_id,
            "customer_name": invoice.title,
            "invoice_number": invoice.invoice_number,
            "date": invoice.date,
            "charge": invoice.invoice_amount,
            "payment_id": None,
            "description": None
        }
        return cls(data)

    @classmethod
    def from_payment(cls, payment):
        invoice = payment.invoice
        data = {
            "type": "payment",
            "invoice_id": invoice.id,
            "customer_id": invoice.customer_id,
            "customer_name": invoice.title,
            "invoice_number": invoice.invoice_number,
            "date": payment.payment_date,
            "credit": payment.amount,
            "payment_id": payment.id,
            "description": None
        }
        return cls(data)

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = INVOICE_COMMON_FIELDS + ['context']
        ordering = ('date', 'created',)