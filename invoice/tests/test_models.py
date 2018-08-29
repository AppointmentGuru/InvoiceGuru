from django.test import TestCase
from django import db
from django.conf import settings
from api.testutils import (
    create_mock_invoice,
    create_mock_v2_invoice,
    create_mock_proof
)
from invoice.models import (
    Invoice,
    InvoiceSettings,
    ProofOfPayment,
    Transaction
)
from .responses import (
    expect_get_appointments,
    expect_get_practitioner_response,
    expect_get_record_response,
    expect_get_user_response
)
from datetime import date
import responses

class InvoiceQuickCreateModelTestCase(TestCase):

    def setUp(self):
        self.invoice = Invoice()
        self.invoice.customer_id = 1
        self.invoice.practitioner_id = 2
        self.invoice.appointments = [3,4,5]
        self.invoice.template = 'basic_v2'

class InvoiceModelTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()
        self.invoice.invoice_amount = 12.34
        self.invoice.integrate_medical_aid = True
        settings = self.invoice.settings
        settings.snap_id = '12345'
        settings.save()

        # need this to count db queries
        settings.DEBUG = True
        db.reset_queries()

    def test_getting_settings_is_cached(self):
        db.reset_queries()
        len(db.connection.queries) == 0
        self.invoice.settings
        len(db.connection.queries) == 1
        self.invoice.settings
        len(db.connection.queries) == 1

    def test_get_snapscan_qr_url(self):
        snap_url = self.invoice.get_snapscan_qr
        self.assertEqual(
            snap_url,
            'https://pos.snapscan.io/qr/12345.svg?invoice_id={}&amount=1234&strict=true'.format(self.invoice.id)
        )

    def test_get_snapscan_link_url(self):
        snap_url = self.invoice.get_snapscan_url
        self.assertEqual(
            snap_url,
            'https://pos.snapscan.io/qr/12345?invoice_id={}&amount=1234&strict=true'.format(self.invoice.id)
        )

    def test_get_serialized(self):
        from ..serializers import INVOICE_COMMON_FIELDS
        self.invoice.date = self.invoice.date
        data = self.invoice._get_serialized()


class ProofOfPaymentTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()
        self.proof = create_mock_proof(self.invoice)

    def test_approve_proof_of_payment(self):
        self.proof.approve()
        self.proof.refresh_from_db()

        assert self.proof.approved == True
        assert self.proof.transaction is not None

class CreateInvoiceFromAppointmentTestCase(TestCase):

    appointment_data = {
        "client": {
            "id": 3,
        },
        "start_time": "2018-07-26T07:00:00Z",
        "end_time": "2018-07-26T16:00:00Z",
        "invoice_title": "This is the invoice title"
    }

    @responses.activate
    def setUp(self):
        self.practitioner_id = 1
        self.appointment_id = 2
        self.customer_id = 3

        # expected requests:
        expect_get_appointments([self.appointment_id], self.practitioner_id, response_data=self.appointment_data)
        expect_get_practitioner_response(self.practitioner_id)
        expect_get_record_response(self.customer_id, self.practitioner_id)
        expect_get_user_response(self.customer_id)

        self.invoice = Invoice.from_appointment(
            self.practitioner_id,
            self.appointment_id
        )
        self.invoice.refresh_from_db()

    def test_create_invoice_from_appointment(self):
        assert self.invoice.id is not None

    def test_it_sets_context(self):

        assert int(self.invoice.customer_id) == int(self.customer_id), \
            'Expected {}. got: {}'.format(self.customer_id, self.invoice.customer_id)

    def test_it_sets_dates(self):

        expected_date = date(2018, 7, 26)

        assert self.invoice.date == expected_date
        assert self.invoice.due_date == expected_date
        assert self.invoice.invoice_period_from == expected_date
        assert self.invoice.invoice_period_to == expected_date


class CreateInvoiceTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_v2_invoice()

    def test_create_invoice(self):
        Invoice.objects.get(id=self.invoice.id)

    def test_invoice_number_generated(self):

        self.invoice.title = 'Joe Soap'
        assert self.invoice.invoice_number == 'JS-{}'.format(self.invoice.id)

    def test_invoice_number_generated_with_no_title(self):
        self.invoice.title = None
        assert self.invoice.invoice_number == 'INV-{}'.format(self.invoice.id)

    def test_it_ignores_letters(self):

        self.invoice.title = "Christo [Test quickinvoice 1]"
        assert self.invoice.invoice_number == 'CQ-{}'.format(self.invoice.id),\
            'Number was: {}'.format(self.invoice.invoice_number)

    def test_password_is_short(self):

        key = self.invoice.admin_invoice_url.split('?')[1]
        assert len(key) == 12,\
            'Expected params to be 12 chars. Expected something like: key=b4c8b930. Got: {}'.format(key)

    @responses.activate
    def test_get_short_url(self):
        url = "https://www.googleapis.com/urlshortener/v1/url"
        url_response = "https://go.gl"
        responses.add(responses.POST, url, json={"id": url_response})
        url = self.invoice.get_short_url()
        self.assertEqual(url, "https://go.gl")
        self.assertEqual(self.invoice.short_url, url)
