from django.test import TestCase
from api.testutils import (
    create_mock_invoice,
    create_mock_proof
)
from invoice.models import (
    Invoice,
    ProofOfPayment,
    Payment
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