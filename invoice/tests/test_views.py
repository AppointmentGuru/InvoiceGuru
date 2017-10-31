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


