from django.core.management.base import BaseCommand
from django.utils.text import slugify
from datetime import datetime
import requests, random, json

BASE_URL = 'https://beta.appointmentguru.co'

'''
curl https://invoice-generator.com \
  -d from="Invoiced, Inc." \
  -d to=Parag \
  -d logo="https://invoiced.com/img/logo-invoice.png" \
  -d number=1 \
  -d date="Feb 9, 2015" \
  -d due_date="Feb 16, 2015" \
  -d items[0][name]="Starter plan monthly" \
  -d items[0][quantity]=1 \
  -d items[0][unit_cost]=99.99 \
  -d notes="Thanks for being an awesome customer!" \
  -d terms="Please pay by the due date." \
> invoice.pdf
'''

class Command(BaseCommand):
    '''
    Set pricing info on legacy appointments
    usage: python manage.py from_guru {auth_token} {from} {to}
    '''
    help = 'Set pricing info on legacy appointments'

    def _get(self, path, token, params={}):
        url = "{}{}".format(BASE_URL, path)
        headers = {
            "Authorization": "Token {}".format(token)
        }
        return requests.get(url, headers=headers, params=params)

    def _lineitem(self, appointment, products):
        product = products.get(appointment.get('product')).get('title')
        dt = appointment.get('start_time').split('T')[0]
        data = {
            'name': '{}: {}'.format(dt, product),
            'unit_cost': float(appointment.get('price'))
        }
        deets = appointment.get('invoice_description', None)
        if deets is not None:
            data.update({'description': deets})
        return data

    def _invoice(self, appointment, profile):

        from_string = '{} {}\n {}' . format(
            profile.get('first_name'),
            profile.get('last_name'),
            '64 2nd ave,\nParkhurst\nJohannesburg'
        )
        full_name = appointment.get('full_name')
        prefix = ''.join([item[0:1].upper() for item in full_name.split(' ')])
        today = datetime.now().strftime('%Y-%m-%d')
        rand = random.choice(range(100,999))
        invoice_number = '{}-{}-{}'.format(prefix, today.replace('-',''), rand)

        to = "Vumatel (Pty) Ltd\nVAT reg: 4020266740 Address:\nPO Box 1811 Parklands\n2121"

        return {
          "from": from_string,
          "to": to,
          "number": invoice_number,
          "currency": "ZAR",
          "date": today,
          # "due_date": '25-04-2017',
          # "logo": profile.get('profile').get('logo_picture'),
          # "notes": "Banking details:\nMumtaz Gani\nFNB\nCheque acc: 62096047678\nBranch code: 252505\n Please use reference: {}".format(invoice_number)
          "notes": "Banking details:\nChristo Crampton\nFNB\nAcc no: 60232195566\nBranch code: 252505\n Please use reference: {}.\nCharged at a rate of R500/hour".format(invoice_number)
        }

    def _to_pdf(self, practitioner, data):
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        pdf = requests.post(
                    'https://invoice-generator.com',
                    json=data,
                    headers=headers
                )
        name = '{}-{}.pdf'.format(slugify(data.get('to')), data.get('number'))
        path = './{}/{}'.format(practitioner, name)
        f = open(path,"wb")
        f.write(pdf.content)
        f.close()
        return name

    def _to_screen(self, data):

        print(data.get('to'))
        for item in data.get('items'):
            print(' - {}. R{}' . format(item.get('name'), item.get('unit_cost')))

    def add_arguments(self, parser):
        '''Params: practitioner_id'''
        parser.add_argument('auth_token')
        parser.add_argument('from')
        parser.add_argument('to')

        parser.add_argument(
            'client',
            default=None,
            help='Only generate invoice for specified client',
        )

    def handle(self, **options):
        '''run the command'''

        token = options.get('auth_token')
        frm = options.get('from')
        to = options.get('to')
        client = options.get('client')

        use_statuses = ['N', 'PR']

        params = {
            "after_utc": frm,
            "before_utc": to
        }
        if client is not None:
            params.update({"client_id": client})

        appointments = self._get('/api/appointments/', token, params)
        profile = self._get('/api/v2/practitioner/me/', token)
        profile = profile.json().get('results')[0]

        clients = set([i.get('client') for i in appointments.json()])
        products = {}

        for service in profile.get('profile').get('services'):
            for product in service.get('products'):
                products.update({ product.get('id'): product })

        # self._lineitems()
        total = 0
        for client in clients:

            lineitems = []
            last_appointment = None
            for appointment in appointments.json():
                status = appointment.get('status')
                app_client = appointment.get('client')

                is_active_client = (app_client == client)
                is_valid_status = (status in use_statuses)
                if is_active_client and is_valid_status:
                    start = appointment.get('start_time')
                    id = appointment.get('id')
                    lineitems.append(self._lineitem(appointment, products))
                    # print (' - #{} [{}] - {}'.format(id, start, status))
                    total += float(appointment.get('price'))
                    last_appointment = appointment
            if last_appointment is not None:
                invoice = self._invoice(last_appointment, profile)
                invoice.update({'items': lineitems})
                self._to_screen(invoice)
                self._to_pdf(profile.get('first_name'), invoice)

        print('------------')
        print('Total: R{}'.format(total))


