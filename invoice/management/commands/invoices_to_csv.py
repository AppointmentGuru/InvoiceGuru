from django.core.management.base import BaseCommand
from django.conf import settings

from invoice.models import Invoice
import csv

class Command(BaseCommand):
    help = 'Download invoices to csv'

    def add_arguments(self, parser):
        parser.add_argument('practitioner_id', nargs='+', type=int)

    def handle(self, *args, **options):
        practitioner_id = options['practitioner_id'][0]
        filename = 'invoices-{}.csv'.format(practitioner_id)
        csvfile = open(filename, 'w+')
        writer = csv.writer(csvfile)

        rows = [
            'title', 'status', 'date', 'due_date',
            'invoice_amount', 'short_url', 'created_date',
            'customer_id', 'appointments',
        ]
        writer.writerow(rows)
        invs = Invoice.objects.filter(practitioner_id=practitioner_id).order_by('date')
        for inv in invs:
            item = []
            for row in rows:
                item.append(getattr(inv, row))
            writer.writerow(item)

