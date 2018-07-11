from django.test import TestCase
from django import db
from django.conf import settings
from api.testutils import (
    create_mock_invoice,
    create_mock_proof
)
from invoice.models import (
    Invoice,
    InvoiceSettings,
    ProofOfPayment,
    Payment
)

class InvoiceModelTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()
        self.invoice.invoice_amount = 12.34
        self.settings = InvoiceSettings()
        self.settings.snap_id = '12345'
        self.settings.practitioner_id = self.invoice.practitioner_id
        self.settings.save()

        # need this to count db queries
        settings.DEBUG = True
        db.reset_queries()

    def test_get_settings_from_invoice(self):
        assert self.settings.id == self.invoice.settings.id

    def test_getting_settings_is_cached(self):
        db.reset_queries()
        len(db.connection.queries) == 0
        self.invoice.settings
        len(db.connection.queries) == 1
        self.invoice.settings
        len(db.connection.queries) == 1

    def test_if_no_settings_exist_return_none(self):
        invoice = create_mock_invoice()
        assert invoice.settings is None

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

class PaymentTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

class ProofOfPaymentTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()
        self.proof = create_mock_proof(self.invoice)

    def test_approve_proof_of_payment(self):
        self.proof.approve()
        self.proof.refresh_from_db()

        assert self.proof.approved == True
        assert self.proof.payment is not None


class CreateInvoiceTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

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

    def test_get_short_url(self):
        url = self.invoice.get_short_url()
        assert self.invoice.short_url == url

    def test_can_manually_update_amount_paid(self):
        self.invoice.amount_paid = 10
        self.invoice.save()

        self.invoice.refresh_from_db()
        assert self.invoice.amount_paid == 10,\
            'Expected amount_paid to be 10. Got: {}'.format(self.invoice.amount_paid)