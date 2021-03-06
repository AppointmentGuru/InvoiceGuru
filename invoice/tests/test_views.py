# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase, override_settings
from django.conf import settings

from api.testutils import create_mock_invoice
import responses

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

    @responses.activate
    @override_settings(KEEN_PROJECT_ID='1234')
    def setUp(self):
        '''
        curl -i -X POST -d 'payload="{\"id\":7,\"status\":\"completed\",\"totalAmount\":1000,\"tipAmount\":0,\"feeAmount\":35,\"settleAmount\":965,\"requiredAmount\":1000,\"date\":\"2018-04-23T13:51:59Z\",\"snapCode\":\"EJrKB_SJ\",\"snapCodeReference\":\"587e9743-3c7c-4e86-b54c-985ca29fe895\",\"userReference\":\"\",\"merchantReference\":\"1765\",\"statementReference\":null,\"authCode\":\"455303\",\"deliveryAddress\":null,\"extra\":{\"amount\":\"1000\",\"invoice_id\":\"1790\"}}"' https://invoiceguru.appointmentguru.co/incoming/snapscan/739B7B5E-B896-4C99-9AF5-AD424DB437A5/
        curl -i -X POST -d 'payload={\"id\":7,\"status\":\"completed\",\"totalAmount\":1000,\"tipAmount\":0,\"feeAmount\":35,\"settleAmount\":965,\"requiredAmount\":1000,\"date\":\"2018-04-23T13:51:59Z\",\"snapCode\":\"EJrKB_SJ\",\"snapCodeReference\":\"587e9743-3c7c-4e86-b54c-985ca29fe895\",\"userReference\":\"\",\"merchantReference\":\"1765\",\"statementReference\":null,\"authCode\":\"455303\",\"deliveryAddress\":null,\"extra\":{\"amount\":\"1000\",\"invoice_id\":\"1790\"}}' http://localhost:8000/incoming/snapscan/739B7B5E-B896-4C99-9AF5-AD424DB437A5/
        '''
        keen_url = 'https://api.keen.io/3.0/projects/{}/events/snapscan_webhook'.format(settings.KEEN_PROJECT_ID)
        print(keen_url)
        responses.add(
            responses.POST,
            url=keen_url,
            json={'ok': 'true'}
        )

        self.url = reverse('incoming_snapscan')
        self.invoice = create_mock_invoice()
        data = {
            "payload": "{\"id\":7,\"status\":\"completed\",\"totalAmount\":1000,\"tipAmount\":0,\"feeAmount\":35,\"settleAmount\":965,\"requiredAmount\":1000,\"date\":\"2018-04-23T13:51:59Z\",\"snapCode\":\"EJrKB_SJ\",\"snapCodeReference\":\"587e9743-3c7c-4e86-b54c-985ca29fe895\",\"userReference\":\"\",\"merchantReference\":\"1765\",\"statementReference\":null,\"authCode\":\"455303\",\"deliveryAddress\":null,\"extra\":{\"amount\":\"1000\",\"invoiceId\":\""+str(self.invoice.id)+"\"}}"
        }
        self.result = self.client.post(self.url, data)

    def test_returns_ok(self):
        assert self.result.status_code == 200

    def test_it_publishes_the_result(self):
        # not sure how to test this
        pass

    def test_updates_invoice_status(self):
        self.invoice.refresh_from_db()
        assert self.invoice.status == 'paid'



