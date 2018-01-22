from django.test import TestCase
from django.urls import reverse
from ..models import Invoice
from api.testutils import create_mock_invoice, assert_response, get_proxy_headers

class ApiRootTestCase(TestCase):

    def test_get_html_root(self):
        response = self.client.get('/', **{'HTTP_ACCEPT':'text/html'})
        response.status_code == 200

    def test_get_html_root_logged_in_via_upstream(self):
        headers = {
            'HTTP_ACCEPT': 'text/html',
            'HTTP_X_ANONYMOUS_CONSUMER': 'false',
            'HTTP_X_AUTHENTICATED_USERID': '1'
        }
        response = self.client.get('/', **headers)
        assert response.status_code == 200, \
            'Expected 200. got: {} {}'.format(
                response.status_code,
                response.context)

class SendEndpointTestCase(TestCase):

    def setUp(self):
        invoice = create_mock_invoice(1, 1)
        url = reverse('invoice-send', args=(invoice.id,))
        data = {
            "to_email": "info@38.co.za"
        }
        self.response = self.client.post(url, **get_proxy_headers(1))
        self.invoice = invoice

    def test_send_ok(self):
        assert_response(self.response)

    def test_invoice_status_is_sent(self):
        self.invoice.refresh_from_db()
        assert self.invoice.status == 'sent'

    def test_sends_invoice_to_customer(self):
        pass


class BulkActionsInvoiceTestCase(TestCase):

    def setUp(self):
        pass
