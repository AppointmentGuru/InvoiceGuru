from invoice.models import Invoice
from django.contrib.auth import get_user_model

from faker import Factory
FAKE = Factory.create()


def get_proxy_headers(user_id, consumer='joesoap', headers = {}):
    is_anon = user_id is None
    headers.update({
        'HTTP_X_ANONYMOUS_CONSUMER': is_anon,
        'HTTP_X_AUTHENTICATED_USERID': user_id,
        'HTTP_X_CONSUMER_USERNAME': consumer
    })
    headers['HTTP_X_CONSUMER_USERNAME'] = consumer

    if user_id is None:
        headers['HTTP_X_ANONYMOUS_CONSUMER'] = 'true'
    else:
        headers['HTTP_X_AUTHENTICATED_USERID'] = str(user_id)
    return headers

def name_address():
    return "{}, {}" . format(FAKE.company(), FAKE.address())

def create_mock_user(username, password='testtest'):
    return get_user_model().objects.create_user(username=username, password=password)

def create_mock_invoice(practitioner_id=None, customer_id=None):

    inv_total = FAKE.numerify()

    data = {
        "practitioner_id": practitioner_id or FAKE.numerify(),
        "customer_id": customer_id or FAKE.numerify(),
        "invoice_number": FAKE.numerify(),
        "context": {
            "practitioner_id": 1,
            "customer_id": 465,
            "invoice_number": "2017-08-26-0.43857747042656614",
            "from_string": name_address(),
            "customer_info": name_address(),
            "invoice_date": "2017-08-26",
            "due_date": "2017-08-26",
            "notes": FAKE.paragraph(),
            "invoice_total": inv_total,
            "total_due": inv_total,
            "total_paid": 0,
            "paid_in_full": False,
            "appointments": [
                {
                    "id": 8298,
                    "title": "Ian Roberts",
                    "status": "N",
                    "currency": "ZAR",
                    "price": "4000.00",
                    "product": 88,
                    "start_time": "2017-08-15T07:00:00Z",
                    "notes": "",
                    "invoice_description": "..",
                    "lineitems": {}
                },
                {
                    "id": 8454,
                    "title": "Ian Roberts",
                    "client": 465,
                    "practitioner": 1,
                    "start_time": "2017-08-15T07:00:00Z",
                    "status": "N",
                    "currency": "ZAR",
                    "price": "1200.00",
                    "product": 88,
                    "notes": ''
                },
                ]
            }
        }

    return Invoice.objects.create(**data)