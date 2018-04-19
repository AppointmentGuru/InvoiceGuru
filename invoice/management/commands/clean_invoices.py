from django.core.management.base import BaseCommand
from invoice.models import Invoice
from invoice.helpers import clean_context

class Command(BaseCommand):

    help = 'Summarize the context for appointments'

    def handle(self, *args, **options):
        invoices = Invoice.objects.order_by('created_date').all()
        # invoices=Invoice.objects.filter(id=1692)

        for invoice in invoices:
            print(invoice.id)
            context = invoice.context
            appts = context.get("appointments", [])
            clean_context(context)
            invoice.context = context
            invoice.save()
