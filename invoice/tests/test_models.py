from django.test import TestCase
from api.testutils import create_mock_invoice
from ..models import Invoice

class CreateInvoiceTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    def test_create_invoice(self):
        Invoice.objects.get(id=self.invoice.id)


