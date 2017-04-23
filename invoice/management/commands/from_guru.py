from django.core.management.base import BaseCommand
from schedule.models import Appointment
from datetime import datetime
import requests, random

class Command(BaseCommand):
    '''
    Set pricing info on legacy appointments
    '''
    help = 'Set pricing info on legacy appointments'

    def add_arguments(self, parser):
        '''Params: practitioner_id'''
        parser.add_argument('auth_token')

    def handle(self, **options):
        '''run the command'''
        today = datetime.today().strftime('%d %b %Y')
        items = [
            {
                "name": "Docker and architecture consultation",
                "quantity": 1,
                "unit_cost": 4000
            },
            {
                "name": "Django for Pros session",
                "quantity": 2,
                "unit_cost": 2000
            },
            {
                "name": "VueJS for Pros session",
                "quantity": 2,
                "unit_cost": 2000
            }
        ]
        '''
        'items[0][name]': "Docker and architecture consultation",
            'items[0][quantity]': 1,
            'items[0][unit_cost]': 4000,
            'items[0][description]': "The best gizmos there are around.",
            'items[1][name]': "Django for Pros session",
            'items[1][quantity]': 2,
            'items[1][unit_cost]': 2000,
            'items[2][name]': "VueJS for Pros session",
            'items[2][quantity]': 2,
            'items[2][unit_cost]': 2000,
        '''
        data = {
            'from': 'Christo Crampton',
            'to': 'Tangent Solutions\nCulross Court, 16 Culross Road, Bryanston',
            'number': random.randint(0,1000),
            'currency': 'ZAR',
            'date': today,
            'logo': 'https://s3.eu-central-1.amazonaws.com/appointmentguru.co/icon-300x300.png',
            'items': items,
            'notes': 'Bank account details: FNB. acc number: 60232195566\nThank-you for your business'
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

