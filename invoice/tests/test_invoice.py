from django.test import TestCase
import json
from django.urls import reverse
from api.testutils import create_mock_invoice

class InvoiceViewTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()
        url = reverse('invoice_view', args=(self.invoice.id,))
        url = "{}?key={}".format(url, self.invoice.password)
        self.response = self.client.get(url)

    def test_is_ok(self):
        assert self.response.status_code == 200

    def test_invoice_in_context(self):
        pass
