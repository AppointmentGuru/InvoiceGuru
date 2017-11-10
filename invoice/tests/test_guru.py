from django.test import TestCase
from api.testutils import create_mock_invoice, assert_response
from .responses import MESSAGE_SUCCESS_RESPONSE
from ..guru import publish, send_invoice
from ..api import InvoiceSerializer

import responses

class GuruTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    def test_publish(self):

        data = InvoiceSerializer(self.invoice).data
        publish('test-key', data)

class InvoiceSendTestCase(TestCase):

    @responses.activate
    def setUp(self):

        responses.add(
            responses.POST,
            'https://communicationguru.appointmentguru.co/communications/',
            json=MESSAGE_SUCCESS_RESPONSE,
            status=201
        )
        self.invoice = create_mock_invoice()
        self.result = send_invoice(self.invoice, 'info@38.co.za')
        self.request = responses.calls[0].request

    def test_send(self):
        assert_response(self.result, 201)

