from invoice.models import Invoice
from faker import Factory
FAKE = Factory.create()

def name_address():
    return "{}, {}" . format(FAKE.name(), FAKE.address())

def create_mock_invoice():

    data = {
        "practitioner_id": FAKE.pyint(),
        "customer_id": FAKE.pyint(),
    }

    return Invoice.objects.create(**data)