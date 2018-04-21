from django.core.management.base import BaseCommand
from django.conf import settings

from invoice.models import Invoice
from invoice.serializers import InvoiceSerializer
from invoice.guru import publish

class Command(BaseCommand):
    help = 'Supplement existing icd10 codes from a json file'

    def handle(self, *args, **options):
        sent_invoices = Invoice.objects.filter(status='sent')
        paid_invoices = Invoice.objects.filter(status='paid')

        for invoice in sent_invoices:
            data = InvoiceSerializer(invoice).data
            summarized = [{"id": appt.get('id')} \
                        for appt \
                        in data.get('context',{}).get('appointments')]
            data.update({"context": { "appointments": summarized } })

            publish(settings.PUBLISHKEYS.invoice_sent, data)

        for invoice in paid_invoices:
            data = InvoiceSerializer(invoice).data
            summarized = [{"id": appt.get('id')} \
                        for appt \
                        in data.get('context',{}).get('appointments')]
            data.update({"context": { "appointments": summarized } })

            publish(settings.PUBLISHKEYS.invoice_paid, data)
