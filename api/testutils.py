from invoice.models import Invoice
from faker import Factory
FAKE = Factory.create()

def name_address():
    return "{}, {}" . format(FAKE.name(), FAKE.address())

def create_mock_invoice():

    data = {
        "from_id": FAKE.pyint(),
        "from_string": name_address(),
        "to_string": name_address(),
        "logo": "https://placeholdit.imgix.net/~text?txtsize=55&txt=logo&w=200&h=200",
        "notes": FAKE.paragraph(),
        "terms": FAKE.paragraph()
    }

    return Invoice.objects.create(**data)