"""
Tasks are simple functions made available to other services via process engine
They encapsulate the critical business capabilities exposed by this service

nb:
* json in, json out!
* __ = private

"""
from django.conf import settings
from invoice.models import Invoice, Payment
from .guru import get_headers
import requests, json

from faker import Factory
FAKE = Factory.create()

from enum import Enum

class Transport(Enum):
    EMAIL = 'email'
    SMS = 'sms'
    INAPP = 'in-app'

class MessageTemplate(Enum):
    SUBMIT_TO_MEDICAL_AID = 'SUBMIT_TO_MEDICAL_AID'
    SEND_RECEIPT = 'SEND_RECEIPT'
    SEND_INVOICE = 'SEND_INVOICE'

def __send_templated_communication(transport, practitioner_id, channel, frm, to, template_slug, context, urls=None, **kwargs):
    headers = get_headers(practitioner_id)
    base = settings.COMMUNICATIONGURU_API
    url = "{}/communications/".format(base)
    data = {
        "channel": channel,
        "context": json.dumps(context),
        "template_slug": template_slug,
    }
    if urls is not None:
        data.update({
            "attached_urls": urls
        })

    # backends should probably not be hard coded:
    if transport == Transport.EMAIL:
        if isinstance(to, str):
            to = [to]
        data.update({
            "sender_email": frm,
            "recipient_emails": to,
            "backends": ["services.backends.email.EmailBackend"]
        })
    if transport == Transport.SMS:
        data.update({
            "recipient_phone_number": to,
            "backends": ["services.backends.zoomconnect.ZoomSMSBackend"]
            })
    if transport == Transport.INAPP:
        data.update({
            "channel": to,
            "recipient_channel": to,
            "backends": ["services.backends.onesignal.OneSignalBackend"]
            })
    print(url)
    print(headers)
    print(data)
    return requests.post(url, data, headers=headers)


def __extract_message_context(data):
    """
    returns from_email, to_email, to_phone_number, invoice_id, invoice
    """
    invoice_id = data.get("invoice_id")
    return (
        data.get("from_email"),
        data.get("to_email"),
        data.get("to_phone_number"),
        invoice_id,
        Invoice.objects.get(id=invoice_id)
    )

def submit_to_medical_aid(data):
    '''
    Forward an invoice on to medical aid
    data = {
        "to_email": "claims@discovery.co.za",
        "from_email": "customer@domain.com",
        "invoice_id": 123
    }
    '''
    from_email, to_email, to_phone_number, invoice_id, invoice = __extract_message_context(data)
    context = {
        "invoice": invoice._get_serialized()
    }
    base = settings.INVOICEGURU_BASE_URL
    invoice_url = "{}{}".format(base, invoice.get_download_url)

    result = __send_templated_communication(
        transport = Transport.EMAIL,
        practitioner_id = invoice.practitioner_id,
        channel = "practitioner-{}".format(invoice.practitioner_id),
        frm = from_email,
        to = to_email,
        template_slug = MessageTemplate.SUBMIT_TO_MEDICAL_AID.value,
        context = context,
        urls = [invoice_url]
    )
    return result.json()

def send_invoice_or_receipt(data):
    '''
    Send an invoice to the user.

    data = {
        "from_email": "joe@soap.com",
        "to_emails": ["jane@soap.com"],
        "to_phone_numbers": ["+27821234567"],
        "to_channels": ["test-channel"],
        "invoice_id": 123
    }
    '''

    invoice_id = data.get("invoice_id")
    from_email = data.get("from_email")
    to_emails = data.get("to_emails")
    to_phone_numbers = data.get("to_phone_numbers")
    to_channels = data.get("to_channels")

    invoice = Invoice.objects.get(id=invoice_id)
    base = settings.INVOICEGURU_BASE_URL
    path = '/invoice/{}/?key={}'.format(invoice.pk, invoice.password)
    invoice_url = "{}{}".format(base, path)

    template = MessageTemplate.SEND_INVOICE.value
    if invoice.is_receipt:
        template = MessageTemplate.SEND_RECEIPT.value

    appointment_object_ids = ['appointment:{}'.format(id) for appt in invoice.appointments]
    object_ids = [
        "practitioner:{}".format(invoice.practitioner_id),
        "customer:{}".format(invoice.customer_id),
        "user:{}".format(invoice.practitioner_id),
        "user:{}".format(invoice.customer_id),
        "invoice:{}".format(invoice.id)
    ]
    object_ids.extend(appointment_object_ids)
    data = {
        "practitioner_id": invoice.practitioner_id,
        "frm": from_email,
        "channel" : "practitioner-{}".format(invoice.practitioner_id),
        "template_slug": template,
        "object_ids": object_ids,
        "context": {
            "invoice": invoice._get_serialized()
        },
        "urls": [invoice_url]
    }
    if to_emails is not None and len(to_emails) > 0:
        email_data = data.copy()
        email_data.update({
            "transport": Transport.EMAIL,
            "to": to_emails
        })
        __send_templated_communication(**email_data)

    if to_phone_numbers is not None:
        for phone in to_phone_numbers:
            sms_data = data.copy()
            sms_data.update({
                "transport": Transport.SMS,
                "to": phone
            })
            __send_templated_communication(**sms_data)

    if to_channels is not None:
        for channel in to_channels:
            channel_data = data.copy()
            channel_data.update({
                "transport": Transport.INAPP,
                "to": channel
            })
            __send_templated_communication(**channel_data)


def mark_invoice_as_paid(data):
    '''
    Mark an invoice as paid and do all the requisite work

    data = {
        "invoice_id": .. ,
        "payment_method": "unknown"
        "options": {
            "send_receipt": False
        }
    }
    '''
    invoice_id = data.get('invoice_id')
    payment_method = data.get("payment_method", "unknown")
    should_send_receipt = data.get("options", {}).get('send_receipt', False)

    invoice = Invoice.objects.get(id=invoice_id)
    invoice.amount_paid = invoice.invoice_amount
    invoice.status = 'paid'
    invoice.save()
    invoice.publish()

    Payment.from_invoice(invoice, payment_method=payment_method)

    if should_send_receipt:
        invoice.send(to_email=True)
    return invoice

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
