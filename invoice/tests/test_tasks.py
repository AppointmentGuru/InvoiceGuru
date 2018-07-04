# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings
from ..tasks import (
    __send_templated_communication as stc,
    submit_to_medical_aid,
    send_invoice_or_receipt
)
from api.testutils import create_mock_invoice
import responses



class TemplatedCommunicationTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    @override_settings(COMMUNICATIONGURU_API='https://communicationguru')
    @responses.activate
    def test_send_templated_communication(self):

        responses.add(
            responses.POST,
            url = 'https://communicationguru/communications/',
            json = {'id': 5},
            status = 201
        )

        data = { "name": "Joe" }
        result = stc(
            "email",
            1,
            "test-channel",
            "tech@appointmentguru.co",
            "info@appointmentguru.co",
            4,
            data
        )
        assert result.status_code == 201
        assert result.json().get('id') == 5

    @override_settings(COMMUNICATIONGURU_API='https://communicationguru')
    @responses.activate
    def test_submit_to_medical_aid_communication(self):
        responses.add(
            responses.POST,
            url = 'https://communicationguru/communications/',
            json = {'id': 5},
            status = 201
        )

        data = {
            "to_email": "tech@appointmentguru.co",
            "from_email": "no-reply@appointmentguru.co",
            "invoice_id": self.invoice.id
        }
        result = submit_to_medical_aid(data)

        assert result.get('id') == 5


class SendInvoiceTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()
        self.payload = {
            "to_emails": ["christo@appointmentguru.co", "christo.crampton@vumatel.co.za"],
            "from_email": ["no-reply@appointmentguru.co"],
            # "to_phone_numbers": ["+27832566533"],
            "to_channels": ["practitioner-1"],
            "invoice_id": self.invoice.id
        }
        result = send_invoice_or_receipt(self.payload)

    # @responses.activate
    # def test_it_sends_emails(self):
    #     pass
