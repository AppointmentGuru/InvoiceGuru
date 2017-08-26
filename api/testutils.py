from invoice.models import Invoice
from faker import Factory
FAKE = Factory.create()

def name_address():
    return "{}, {}" . format(FAKE.name(), FAKE.address())

def create_mock_invoice():

    data = {
        "practitioner_id": 1,
        "customer_id": 465,
        "context": {
            "practitioner_id": 1,
            "customer_id": 465,
            "invoice_number": "2017-08-26-0.43857747042656614",
            "from_string": "Practitioners addr",
            "customer_info": "Customer's addr",
            "invoice_date": "2017-08-26",
            "due_date": "2017-08-26",
            "notes": "some bank",
            "invoice_total": 0,
            "total_due": 0,
            "total_paid": 0,
            "paid_in_full": false,
            "appointments": [
                {
                    "id": 8298,
                    "start_time": "2017-08-02T07:00:00Z",
                    "end_time": "2017-08-02T15:00:00Z",
                    "title": "Ian Roberts",
                    "client": 465,
                    "practitioner": 1,
                    "status": "N",
                    "currency": "ZAR",
                    "price": "4000.00",
                    "product": 88,
                    "notes": {},
                    "invoice_description": "..",
                    "included": true,
                    "lineitems": {}
                },
                {
                    "id": 8454,
                    "start_time": "2017-08-03T14:00:00Z",
                    "end_time": "2017-08-03T16:00:00Z",
                    "title": "Ian Roberts",
                    "client": 465,
                    "practitioner": 1,
                    "status": "N",
                    "currency": "ZAR",
                    "price": "1200.00",
                    "product": 88,
                    "notes": {},
                    "included": true,
                    "lineitems": {
                        "0": {
                            "id": 11,
                            "owners": {
                                "0": "1"
                            },
                            "object_ids": {
                                "0": "appointment:8454"
                            },
                            "fields": {
                                "0": "icd10",
                                "1": "tariff",
                                "2": "price"
                            },
                            "values": {
                                "0": {
                                    "0": "123",
                                    "1": "Abc",
                                    "2": "123"
                                }
                            }
                        }
                    }
                },
                ]
            }
        }

    return Invoice.objects.create(**data)