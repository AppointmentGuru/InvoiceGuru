'''
API for AppointmentGuru microservices
'''
import requests, json
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
        'HTTP_X_ANONYMOUS_CONSUMER': 'False',
        'HTTP_X_AUTHENTICATED_USERID': user_id,
        'HTTP_X_CONSUMER_USERNAME': consumer,
    }

def send_invoice(invoice, to, transport='email'):
    url = '{}/communications/'.format(settings.COMMUNICATIONGURU_API)

    # invoice_url = "{}/invoice/{}/?key={}"\
    #                 .format(settings.INVOICEGURU_BASE_URL,
    #                         invoice.id,
    #                         invoice.password)
    invoice_url = invoice.admin_invoice_url
    invoice_date = invoice.context.get('due_date')
    subject = 'Your invoice for {}'.format(invoice_date)
    message = """Hi

Attached please find your invoice for {}.
You can also view it online at:
{}
""".format(invoice_date, invoice_url)

    object_ids = [
        'user:{}'.format(invoice.practitioner_id),
        'user:{}'.format(invoice.customer_id)
    ]
    object_ids = object_ids + invoice.object_ids
    from_email = invoice.sender_email
    data = {
        "owner": invoice.practitioner_id,
        "object_ids": object_ids,
        "subject": subject,
        "message": message,
        "preferred_transport": transport,
        "attached_urls": [invoice_url],
        "recipient_emails": [to],
        "sender_email": from_email
    }

    return requests.post(url, json=data, headers=get_headers(invoice.practitioner_id))
