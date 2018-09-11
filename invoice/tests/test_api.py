from django.test import TestCase, override_settings
from django.urls import reverse
from ..models import Invoice
from api.testutils import (
    assert_response,
    get_proxy_headers,
    create_mock_v2_invoice,
    create_mock_settings
)
from .responses import (
    expect_shorten_url,
    expect_communications_response
)
from unittest import mock
import responses

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

    # @mock.patch('invoice.tasks.send_templated_communication')
    @mock.patch.object(Invoice, 'publish')
    def setUp(self, publish_mock):

        invoice = create_mock_v2_invoice(1, 1)
        expect_shorten_url()

        url = reverse('invoice-send', args=(invoice.id,))
        data = {
            "to_email": "info@38.co.za"
        }
        with responses.RequestsMock() as rsps:
            expect_communications_response(responses_mock=rsps)
            self.response = self.client.post(url, **get_proxy_headers(1))
            # self.call_list = rsps.CallList
        self.invoice = invoice
        self.publish_mock = publish_mock
        # self.templated_mock = templated_mock

    def test_send_ok(self):
        assert_response(self.response)

    def test_invoice_status_is_sent(self):
        self.invoice.refresh_from_db()
        assert self.invoice.status == 'sent'

    def test_it_publishes_update(self):
        self.publish_mock.assert_called()

    def test_sends_invoice_to_customer(self):
        pass

# @override_settings(PUB_SUB_BACKEND=('backends', 'MockBackend'))
class MarkAsPaidEndpointTestCase(TestCase):

    @mock.patch.object(Invoice, 'publish')
    def setUp(self, publish_mock):
        self.invoice = create_mock_v2_invoice(1, 1)
        url = reverse('invoice-paid', args=(self.invoice.id,))
        self.response = self.client.post(url, **get_proxy_headers(1))
        self.invoice.refresh_from_db()
        self.publish_mock = publish_mock

    def test_it_publishes_update(self):
        self.publish_mock.assert_called()

    def test_is_ok(self):
        assert self.response.status_code == 200,\
            'Expected 200. Got: {}: {}'.format(self.response.status_code, self.response)

    def test_creates_payment(self):
        num_payments = self.invoice.transaction_set.filter(type='Payment').count()
        assert num_payments == 1,\
            'Expected exactly 1 payment to be created. Got: {}'.format(num_payments)

    def test_updates_invoice_status_to_paid(self):
        assert self.invoice.status == 'paid'

    def test_sets_amount_paid(self):
        assert self.invoice.amount_paid == self.invoice.invoice_amount

    def test_publishes_result(self):

        # not sure how to test this
        pass

class TransactionListTestCase(TestCase):

    def setUp(self):
        self.headers = get_proxy_headers(1)
        self.url = reverse('transaction-list')

    def test_filter_with_customer_id(self):
        data = {
            "customer_id": 1
        }
        res = self.client.get(self.url, data, **self.headers)

class InvoiceSettingsViewTestCase(TestCase):

    def setUp(self):
        self.practitoner_id = 1
        self.headers = get_proxy_headers(self.practitoner_id)
        create_mock_settings(self.practitoner_id, with_save=True)
        create_mock_settings(3, with_save=True)
        create_mock_settings(3, with_save=True)

    def test_get_my_settings(self):
        url = reverse('invoicesettings-detail', args=('me',))
        result = self.client.get(url, **self.headers)

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json().get('practitioner_id'), str(self.practitoner_id))

    def test_list_only_returns_my_settings(self):
        url = reverse('invoicesettings-list')
        result = self.client.get(url, **self.headers)
        num_results = result.json().get('count')
        self.assertEqual(num_results, 1)

    def test_cannot_get_other_practitioners_settings(self):
        url = reverse('invoicesettings-list')
        result = self.client.get(url, **get_proxy_headers(2))
        num_results = result.json().get('count')
        self.assertEqual(num_results, 0)

