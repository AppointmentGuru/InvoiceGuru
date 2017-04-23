"""
Generate a pdf invoice:

curl -i https://invoice-generator.com \
  -d from="Invoiced, Inc.%0AVAT ID: 1234" \
  -d to="Jared%0AVAT ID: 4567" \
  -d logo="https://invoiced.com/img/logo-invoice.png" \
  -d number=1 \
  -d date="Feb 9, 2015" \
  -d payment_terms="Charged - Do Not Pay" \
  -d items[0][name]="Starter Plan Monthly" \
  -d items[0][quantity]=1 \
  -d items[0][unit_cost]=99 \
  -d items[1][name]="Starter Plan Monthly" \
  -d items[1][quantity]=1 \
  -d items[1][unit_cost]=99 \
  -d items[2][name]="Starter Plan Monthly" \
  -d items[2][quantity]=2 \
  -d items[2][unit_cost]=99 \
  -d tax_title="VAT" \
  -d fields[tax]="%" \
  -d tax=8 \
  -d currency="ZAR" \
  -d notes="Thanks for being an awesome customer!" \
  -d terms="No need to submit payment. You will be auto-billed for this invoice." \
> invoice.vat.pdf && open invoice.vat.pdf

"""
from django.core.management.base import BaseCommand
from datetime import datetime
import requests, random

class Command(BaseCommand):
    '''
    Set pricing info on legacy appointments
    '''
    help = 'Set pricing info on legacy appointments'

    def add_arguments(self, parser):
        '''Params: practitioner_id'''
        parser.add_argument('practitioner_id', type=int)

    def handle(self, **options):
        '''run the command'''
        today = datetime.today().strftime('%d %b %Y')
        data = {
          "from": "Christo Crampton\n64 2nd ave, Parkhurst, Johannesburg",
          "to": "Tangent Solutions\nCulross Court, 16 Culross road, Bryanston, Johannesburg",
          "number": "INV-2",
          "currency": "ZAR",
          "date": "2017-04-25",
          "items": [
            {
              "name": "[2017-03-03] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "Building APIs with Python, Django and Django Rest Framework"
            },
            {
              "name": "[2017-03-03] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "VusJS for Professionals"
            },
            {
              "name": "[2017-03-06] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "Vodacom consultation"
            },
            {
              "name": "[2017-03-29] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "Building APIs with Python, Django and Django Rest Framework"
            },
            {
              "name": "[2017-03-29] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "VusJS for Professionals"
            },
            {
              "name": "[2017-04-06] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "Building APIs with Python, Django and Django Rest Framework"
            },
            {
              "name": "[2017-04-06] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "VusJS for Professionals"
            },
            {
              "name": "[2017-04-24] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "Building APIs with Python, Django and Django Rest Framework"
            },
            {
              "name": "[2017-04-24] consultation",
              # "quantity": 1,
              "unit_cost": "4000.00",
              "description": "VusJS for Professionals"
            }
          ],
          "notes": "Account details: \nBank: FNB, \nBranch code: 250655\nAccount number: 60232195566"
        }
        headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
        pdf = requests.post(
                    'https://invoice-generator.com',
                    json=data,
                    headers=headers
                )
        f = open("invoice.pdf","wb")
        f.write(pdf.content)
        f.close()

        practitioner_id = options['practitioner_id']

