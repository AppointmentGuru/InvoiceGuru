from django.core.management.base import BaseCommand
from invoice.models import Invoice
from invoice.helpers import clean_context
from invoice.invoicebuilder import InvoiceBuilder

class Command(BaseCommand):

    help = 'Summarize the context for appointments'

    def handle(self, *args, **options):
        invoices = Invoice.objects.all()
        # invoices=Invoice.objects.filter(id=1692)

        for invoice in invoices:
            print(invoice.id)
            builder = InvoiceBuilder(invoice)
            builder.populate_appointments_from_context()
            builder.enrich(save_context=True)
