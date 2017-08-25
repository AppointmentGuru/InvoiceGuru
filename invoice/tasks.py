from django.conf import settings
import requests
from faker import Factory
FAKE = Factory.create()

def generate_invoice_number(invoice):
    invoice_number = '{}{}{}' . format(
        invoice.to_id,
        invoice.id,
        FAKE.pyint())
    return invoice_number

def generate_pdf(invoice):

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

    data = {
        'from': invoice.from_string,
        'to': invoice.to_string,
        'number': invoice.invoice_number,
        'currency': invoice.currency,
        'date': invoice.date.isoformat().split('T')[0],
        'logo': invoice.logo,
        'items': items,
        'notes': invoice.notes
    }
    headers = {'Content-Type': 'application/json', 'Accept':'application/json'}
    pdf = requests.post(
                settings.INVOICE_GENERATOR_URL,
                json=data,
                headers=headers
            )
    invoice_name = '{}-{}-{}.pdf' . format(invoice.from_id, invoice.date, invoice.id)
    invoice_path = "{}{}".format(settings.MEDIA_ROOT, invoice_name)
    f = open(invoice_path,"wb")
    f.write(pdf.content)
    f.close()
    return invoice_path
