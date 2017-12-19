from django.core.management.base import BaseCommand
from datetime import datetime, date
from invoice.helpers import get_appointments_in_range, \
                            prepare_appointments_for_construction,\
                            get_headers
import calendar

class Command(BaseCommand):
    help = 'Generate invoices for practitioners'

    def handle(self, *args, **options):
        now = datetime.now()
        now = date(2017, 8, 1)
        first = now.replace(day=1)
        last = now.replace(day=calendar.monthrange(now.year, now.month)[1])

        first_string = first.strftime('%Y-%m-%d')
        last_string = last.strftime('%Y-%m-%d')

        practitioners = [1]

        for practitioner in practitioners:

            appts = get_appointments_in_range(
                        practitioner,
                        first_string,
                        last_string)
            construction_input = prepare_appointments_for_construction(appts)

            for client, appointments in construction_input.items():

                host = 'http://localhost'
                path = '/invoices/construct/'
                params = {
                    'practitioner_id': practitioner,
                    'appointment_ids': (",").join([str(i) for i in appointments]),
                    "client_id": client
                }
                context = {
                    "due_date": last_string,
                    "date": last_string,
                    "invoice_period_from": first_string,
                    "invoice_period_to": last_string
                }
                url = "{}{}".format(host, path)
                result = request.get(url, headers=get_headers(), params=params)
                import ipdb;ipdb.set_trace()


