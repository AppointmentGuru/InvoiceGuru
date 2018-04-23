# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase

from api.testutils import create_mock_invoice


class InvoiceViewTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()
        self.url = reverse('invoice_view', args=(self.invoice.pk,))

    def test_get_without_password(self):
        self.result = self.client.get(self.url)
        assert self.result.status_code == 404,\
            'Expected 404 when accessing invoice view page without password'

    def test_get_with_password(self):
        url = '{}?key={}'.format(self.url, self.invoice.password)
        self.result = self.client.get(url)
        assert self.result.status_code == 200

    def test_get_with_customer_password(self):
        '''When getting the page with the customer password, set views = True'''
        print ('TBD')

class SnapScanWebHookTestCase(TestCase):

    def setUp(self):
        self.url = reverse('incoming_snapscan')

    def test_post_to_webhook(self):

        data = {
            "id": 1,
            "status": "completed",
            "date": "1999-12-31T23:00:00Z",
            "totalAmount": 1000,
            "tipAmount": 0,
            "requiredAmount": 1000,
            "snapCode": "STB115",
            "snapCodeReference": "Till Point #1",
            "userReference": "John Doe",
            "merchantReference": "INV001",
            "statementReference": "SNAPSCAN 20150109",
            "authCode": "123456",
            "extra": None,
            "deliveryAddress": None
        }
        result = self.client.post(self.url, data)
        assert result.status_code == 200


