from django.test import TestCase
from api.testutils import create_mock_invoice
from ..models import Invoice

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