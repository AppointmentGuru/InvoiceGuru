from django.test import TestCase
from api.testutils import create_mock_invoice
from ..guru import publish
from ..api import InvoiceSerializer

class GuruTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    def test_publish(self):

        data = InvoiceSerializer(self.invoice).data
        publish('test-key', data)