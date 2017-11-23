from django.test import TestCase
from api.testutils import create_mock_invoice, assert_response
from .responses import MESSAGE_SUCCESS_RESPONSE
from ..guru import publish, send_invoice
from ..api import InvoiceSerializer

import responses, json

class GuruTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    def test_publish(self):

        data = InvoiceSerializer(self.invoice).data
        publish('test-key', data)

class InvoiceSendTestCase(TestCase):

    def __add_response(self):
        responses.add(
            responses.POST,
            'http://communicationguru/communications/',
            json=MESSAGE_SUCCESS_RESPONSE,
            status=201
        )

    def setUp(self):
        self.invoice = create_mock_invoice()

    @responses.activate
    def test_send_email(self):
        self.__add_response()
        test_to_email = 'info@38.co.za'
        result = send_invoice(self.invoice, test_to_email)
        assert_response(result, 201)

        data = json.loads(result.request.body)
        assert data.get('preferred_transport') == 'email'
        assert data.get('recipient_emails') == [test_to_email]

    @responses.activate
    def test_send_sms(self):
        self.__add_response()
        test_phone_number = '+27832566533'
        result = send_invoice(self.invoice, to_phone=test_phone_number)

        data = json.loads(result.request.body)

        assert data.get('preferred_transport') == 'sms'
        assert data.get('recipient_phone_number') == test_phone_number
