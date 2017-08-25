from django.test import TestCase
import json

class InvoiceViewTestCase(TestCase):

    def setUp(self):
        self.data = {
            "invoice_number": "12345"
        }
        self.response = self.client.post('/invoice/', json.dumps(self.data), content_type='application/json')

    def test_is_ok(self):
        assert self.response.status_code == 200

    def test_post_data_overwrites_default_data(self):

        assert self.response.context['invoice_number'] == self.data.get('invoice_number')

