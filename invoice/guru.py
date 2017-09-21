'''
API for AppointmentGuru microservices
'''
import requests
from django.conf import settings
from pubsub import get_backend

def publish(key, payload):
    '''Send a message onward'''
    pubsub = get_backend(
        settings.PUB_SUB_BACKEND[0],
        settings.PUB_SUB_BACKEND[1],
        settings.PUB_SUB_CHANNEL)
    return pubsub.publish(key, payload)

def get_headers(user_id, consumer='appointmentguru'):
    return {
        'HTTP_X_ANONYMOUS_CONSUMER': False,
        'HTTP_X_AUTHENTICATED_USERID': user_id,
        'HTTP_X_CONSUMER_USERNAME': consumer
    }

def send_invoice(invoice, to, transport='email'):
    url = '{}/service/'.format(settings.FUNCTIONGURU_URL)

    invoice_url = "https://invoiceguru.appointmentguru.co/invoice/{}/"\
                    .format(invoice.id)
    invoice_date = invoice.context.get('due_date')
    subject = 'Your invoice for {}'.format(invoice_date)
    message = """Hi

Attached please find your invoice for {}.
You can also view it online at:
{}
""".format(invoice_date, invoice_url)

    command = "hug -f api.py -c handle {} {} '{}' '{}'"\
        .format(
            to,
            invoice_url,
            subject,
            message
        )

    data = {
        "slug": "send_invoice",
        "command": command
    }
    return requests.post(url, data)
