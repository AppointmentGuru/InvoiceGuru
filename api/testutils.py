from invoice.models import Invoice, ProofOfPayment, InvoiceSettings
from django.contrib.auth import get_user_model
import django
from unittest.mock import Mock
from invoice.tests.responses import (
    expect_get_practitioner_response,
    expect_get_user_response,
    expect_get_record_response,
    expect_get_appointments
)
import responses

from faker import Factory
FAKE = Factory.create()

def assert_response(response, expected_status=200):
    assert response.status_code == expected_status, \
        'Expected status: {}. Got: {}. {}'.format(expected_status, response.status_code, response.content)

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

def create_mock_proof(invoice):
    mock_file = Mock(spec=django.core.files.File)
    mock_file.read.return_value = "fake file contents"
    mock_file.name = 'some_file.pdf'
    proof = ProofOfPayment()
    proof.invoice = invoice
    # proof.document = mock_file
    return proof

def create_mock_settings(practitioner_id):
    settings = InvoiceSettings()
    settings.billing_address = 'billing address'
    settings.invoice_notes = 'invoice note'
    settings.receipt_notes = 'receipt_note'
    settings.integrate_medical_aid = True
    settings.show_snapcode_on_invoice = True
    settings.allow_pre_payments = True
    settings.allow_submit_to_medical_aid = True
    settings.snap_id = 'snappers'
    return settings

@responses.activate
def create_mock_v2_invoice(customer_id=1, practitioner_id=2, appointments=[3,4,5], invoice_data={}, extra_data={}):
    data = {
        "customer_id": 1,
        "practitioner_id": 2,
        "appointments": [3,4,5],
    }
    data.update(invoice_data)

    expect_get_practitioner_response(2)
    expect_get_user_response(1, response_data=extra_data.get("user"))
    expect_get_record_response(1, 2)
    expect_get_appointments([3,4,5], 2, response_data=extra_data)

    invoice = Invoice.objects.create(**data)
    return invoice

def create_mock_invoice(practitioner_id=None, customer_id=None):
    return create_mock_v2_invoice(customer_id=customer_id, practitioner_id=practitioner_id)

    # inv_total = FAKE.numerify()
    # data = {
    #     "practitioner_id": practitioner_id or FAKE.numerify(),
    #     "customer_id": customer_id or FAKE.numerify(),
    #     "sender_email": "support@appointmentguru.co",
    #     "context": {
    #             "notes": "",
    #             "due_date": "2017-09-14",
    #             "total_due": 0,
    #             "total_paid": 0,
    #             "customer_id": 655,
    #             "practice_name": "ACME Consulting",
    #             "from_string": "Sarah Eatwell\nE-mail: tech@appointmentguru.co\nPhone: +27832566533\n",
    #             "appointments": [{
    #                 "id": 8148,
    #                 "notes": None,
    #                 "price": "326.00",
    #                 "title": "Mathew",
    #                 "client": 655,
    #                 "status": "N",
    #                 "product": 45,
    #                 "currency": "ZAR",
    #                 "end_time": "2017-08-10T13:15:00Z",
    #                 "included": True,
    #                 "full_name": "Joe Soap",
    #                 "lineitems": [{
    #                     "id": 16,
    #                     "fields": ["icd10", "procedureCode"],
    #                     "owners": ["363"],
    #                     "values": [
    #                         ["M25.12", "91923, 91929, 91931"]
    #                     ],
    #                     "object_ids": ["appointment:8148"]
    #                 }],
    #                 "codes": [{'appointment': 11378,
    #                     'currency': 'ZAR',
    #                     'description': None,
    #                     'icd10': 'M62.50',
    #                     'id': 394,
    #                     'nappi': None,
    #                     'price': '162.50',
    #                     'procedure': None,
    #                     'process': '91901'},
    #                     {'appointment': 11378,
    #                     'currency': 'ZAR',
    #                     'description': None,
    #                     'icd10': 'M22.4',
    #                     'id': 396,
    #                     'nappi': None,
    #                     'price': '162.50',
    #                     'procedure': None,
    #                     'process': '91922'},
    #                     {'appointment': 11378,
    #                     'currency': 'ZAR',
    #                     'description': None,
    #                     'icd10': 'M25.68',
    #                     'id': 395,
    #                     'nappi': None,
    #                     'price': '162.50',
    #                     'procedure': None,
    #                     'process': '91908'},
    #                     {'appointment': 11378,
    #                     'currency': 'ZAR',
    #                     'description': None,
    #                     'icd10': 'M25.58',
    #                     'id': 397,
    #                     'nappi': None,
    #                     'price': '162.50',
    #                     'procedure': None,
    #                     'process': '91917'}
    #                 ],
    #                 "start_time": "2017-08-10T12:45:00Z",
    #                 "practitioner": 363,
    #                 "invoice_description": None
    #             }, {
    #                 "id": 8147,
    #                 "notes": None,
    #                 "price": "326.00",
    #                 "title": "Mathew",
    #                 "client": 655,
    #                 "status": "C",
    #                 "product": 45,
    #                 "currency": "ZAR",
    #                 "end_time": "2017-08-17T13:15:00Z",
    #                 "included": True,
    #                 "full_name": "Mathew",
    #                 "lineitems": [],
    #                 "start_time": "2017-08-17T12:45:00Z",
    #                 "practitioner": 363,
    #                 "invoice_description": None
    #             }, {
    #                 "id": 8149,
    #                 "notes": None,
    #                 "price": "326.00",
    #                 "title": "Mathew",
    #                 "client": 655,
    #                 "status": "N",
    #                 "product": 45,
    #                 "currency": "ZAR",
    #                 "end_time": "2017-08-24T13:15:00Z",
    #                 "included": True,
    #                 "full_name": "Mathew",
    #                 "lineitems": [{
    #                     "id": 14,
    #                     "fields": ["icd10", "procedureCode"],
    #                     "owners": ["363"],
    #                     "values": [
    #                         ["M25.57", "91923, 91929, 91931"]
    #                     ],
    #                     "object_ids": ["appointment:8149"]
    #                 }],
    #                 "codes": [],
    #                 "start_time": "2017-08-24T12:45:00Z",
    #                 "practitioner": 363,
    #                 "invoice_description": None
    #             }, {
    #                 "id": 8150,
    #                 "notes": None,
    #                 "price": "326.00",
    #                 "title": "Mathew",
    #                 "client": 655,
    #                 "status": "N",
    #                 "product": 45,
    #                 "currency": "ZAR",
    #                 "end_time": "2017-08-31T13:15:00Z",
    #                 "included": True,
    #                 "full_name": "Mathew",
    #                 "lineitems": [{
    #                     "id": 15,
    #                     "fields": ["icd10", "procedureCode"],
    #                     "owners": ["363"],
    #                     "values": [
    #                         ["M25.57", "91923, 91929, 91931"]
    #                     ],
    #                     "object_ids": ["appointment:8150"]
    #                 }],
    #                 "codes": [{'appointment': 11378,
    #                     'currency': 'ZAR',
    #                     'description': None,
    #                     'icd10': 'M62.50',
    #                     'id': 394,
    #                     'nappi': None,
    #                     'price': '162.50',
    #                     'procedure': None,
    #                     'process': '91901'},
    #                     {'appointment': 11378,
    #                     'currency': 'ZAR',
    #                     'description': None,
    #                     'icd10': 'M22.4',
    #                     'id': 396,
    #                     'nappi': None,
    #                     'price': '162.50',
    #                     'procedure': None,
    #                     'process': '91922'},
    #                     {'appointment': 11378,
    #                     'currency': 'ZAR',
    #                     'description': None,
    #                     'icd10': 'M25.68',
    #                     'id': 395,
    #                     'nappi': None,
    #                     'price': '162.50',
    #                     'procedure': None,
    #                     'process': '91908'},
    #                     {'appointment': 11378,
    #                     'currency': 'ZAR',
    #                     'description': None,
    #                     'icd10': 'M25.58',
    #                     'id': 397,
    #                     'nappi': None,
    #                     'price': '162.50',
    #                     'procedure': None,
    #                     'process': '91917'}
    #                 ],
    #                 "start_time": "2017-08-31T12:45:00Z",
    #                 "practitioner": 363,
    #                 "invoice_description": None
    #             }],
    #             "invoice_date": "2017-09-14",
    #             "paid_in_full": False,
    #             "patient_info": "Joe Soap\n",
    #             "customer_info": "Jane Soap\n16 Some place, Somewhere, Johannesburg, 2196",
    #             "invoice_total": 0,
    #             "invoice_number": "2017-09-14-3139",
    #             "banking_details": "Sarah Eatwell\nBank of AppointmentGuru\n252505\nCheque Account\1234567890",
    #             "medicalaid_info": "Medical Aid: Discovery\nMedical Aid Number: 123456789\nMain Member: Jane Soap\n",
    #             "practitioner_id": 363
    #         }
    #     }
    # return Invoice.objects.create(**data)
