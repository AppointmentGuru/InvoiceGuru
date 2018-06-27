from django.core.management.base import BaseCommand
from django.conf import settings

from invoice.models import Invoice, Payment

class Command(BaseCommand):
    help = 'Generate a payments backlog.'

    def handle(self, *args, **options):
        # get all paid invoices
        paid_invoices = Invoice.objects.filter(status='paid', practitioner_id=1)

        print ("Found {} invoices" .format(paid_invoices.count()))

        for invoice in paid_invoices:
            Payment.from_invoice(invoice)