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
          "from": "Kirsten Lawlor Biokineticist\nPractice number: 0290548\n34 Ashford road, Parkwood",
          "to": "Joe Soap, \nSome address, somewhere",
          "number": "INV-2",
          "currency": "ZAR",
          "date": "2017-04-25",
          "logo": "http://beta.appointmentguru.co/media/practitioner/profile/kirsten-lawlor.jpg",
          "items": [
            {
              "name": "21 Jan 2016",
              "quantity": 1,
              "unit_cost": "92",
              "description": "Treatment code: 91923, ICD10 code: M54.57"
            },
            {
              "name": "21 Jan 2016",
              "quantity": 1,
              "unit_cost": "80",
              "description": "Treatment code: 91926, ICD10 code: M54.57"
            },
            {
              "name": "21 Jan 2016",
              "quantity": "1",
              "unit_cost": "80",
              "description": "Treatment code: 91927, ICD10 code: M54.57"
            },
            {
              "name": "25 Jan 2016",
              "quantity": "1",
              "unit_cost": "92",
              "description": "Treatment code: 91923, ICD10 code: M54.57"
            },
            {
              "name": "25 Jan 2016",
              "quantity": "1",
              "unit_cost": "80",
              "description": "Treatment code: 91926, ICD10 code: M54.57"
            },
            {
              "name": "25 Jan 2016",
              "quantity": "1",
              "unit_cost": "80",
              "description": "Treatment code: 91927, ICD10 code: M54.57"
            },
            {
              "name": "28 Jan 2016",
              "quantity": "1",
              "unit_cost": "92",
              "description": "Treatment code: 91927, ICD10 code: M54.57"
            },
            {
              "name": "28 Jan 2016",
              "quantity": "1",
              "unit_cost": "80",
              "description": "Treatment code: 91933, ICD10 code: M54.57"
            },
            {
              "name": "28 Jan 2016",
              "quantity": "1",
              "unit_cost": "80",
              "description": "Treatment code: 91923, ICD10 code: M54.57"
            }
          ],
          "notes": "Account details:\nBank: FNB, Branch code: 250655, Account number: 1234567890\nPlease use reference no: ABC-1234\nE-mail proof of payment to: kirsten@appointmentguru.co, use your reference no. as the subject line\nBook your next appointment online at: http://bookme.guru/kirstenlawlor/",
          "due_date": "2017-05-24"
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

