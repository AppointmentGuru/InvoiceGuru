from django.test import TestCase, override_settings
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

# @override_settings(PUB_SUB_BACKEND=('backends', 'MockBackend'))
class MarkAsPaidEndpointTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice(1, 1)
        url = reverse('invoice-paid', args=(self.invoice.id,))
        self.response = self.client.post(url, **get_proxy_headers(1))
        self.invoice.refresh_from_db()

    def test_is_ok(self):
        assert self.response.status_code == 200,\
            'Expected 200. Got: {}: {}'.format(self.response.status_code, self.response)

    def test_creates_payment(self):
        num_payments = self.invoice.payment_set.count()
        assert num_payments == 1,\
            'Expected exactly 1 payment to be created. Got: {}'.format(num_payments)

    def test_updates_invoice_status_to_paid(self):
        assert self.invoice.status == 'paid'

    def test_sets_amount_paid(self):
        assert self.invoice.amount_paid == self.invoice.invoice_amount

    def test_publishes_result(self):

        # not sure how to test this
        pass



class BulkActionsInvoiceTestCase(TestCase):

    def setUp(self):
        pass
