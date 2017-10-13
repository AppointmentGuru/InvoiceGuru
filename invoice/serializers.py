from rest_framework import serializers
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'practitioner_id', 'customer_id', 'title', 'status', 'context', 'template', 'password']
