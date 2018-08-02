from django.core.management.base import BaseCommand
from django.conf import settings

from invoice.models import Invoice, Transaction

class Command(BaseCommand):
    help = 'Generate a payments backlog.'

    def handle(self, *args, **options):
        # get all sent invoices
        [p.delete() for p in Transaction.objects.all()]

        # create a transaction for all send and paid invoices
        for invoice in Invoice.objects.filter(status__in=['sent', 'paid']):

            # fake status to sent so as to create an invoice transaction entry:
            if invoice.status == 'paid':
                invoice.status = 'sent'
            Transaction.from_invoice(invoice, date=invoice.date)

        for invoice in Invoice.objects.filter(status='paid'):
            Transaction.from_invoice(invoice)

