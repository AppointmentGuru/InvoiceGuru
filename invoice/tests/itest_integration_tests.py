# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase
from testutils import create_mock_invoice

class IntegrationTestCase(TestCase):

    def setUp(self):
        url = reverse('..-list|detail')
        self.result = self.client.get(url)

    def test_send_invoice(self):
        pass

    def test_send_receipt(self):
        pass

    def test_send_to_medical_aid(self):
        pass

