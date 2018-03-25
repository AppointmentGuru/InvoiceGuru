from django.core.management.base import BaseCommand
from django.conf import settings

from invoice.models import Invoice
from invoice.serializers import InvoiceSerializer

import json

class Command(BaseCommand):
    help = 'Supplement existing icd10 codes from a json file'

    def handle(self, *args, **options):

        for invoice in Invoice.objects.filter(status='sent'):
            data = InvoiceSerializer(invoice).data
            summarized = [{"id": appt.get('id')} \
                        for appt \
                        in data.get('context',{}).get('appointments')]
            data.update({"context": { "appointments": summarized } })

            publish(settings.PUBLISHKEYS.invoice_sent, data)

        for invoice in Invoice.objects.filter(status='paid'):
            data = InvoiceSerializer(invoice).data
            summarized = [{"id": appt.get('id')} \
                        for appt \
                        in data.get('context',{}).get('appointments')]
            data.update({"context": { "appointments": summarized } })

            publish(settings.PUBLISHKEYS.invoice_paid, data)
