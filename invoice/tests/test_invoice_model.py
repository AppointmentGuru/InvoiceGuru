# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase
from decimal import Decimal

from api.testutils import (
    create_mock_v2_invoice,
    create_mock_settings
)

from ..models import Invoice, InvoiceSettings, Transaction

import responses

class MinimalInvoiceCreationTestCase(TestCase):

    def setUp(self):
        self.practitioner_id = 1
        self.settings = create_mock_settings(self.practitioner_id)
        self.invoice = create_mock_v2_invoice(self.practitioner_id)

    def test_it_applies_settings(self):
        pass


class InvoicePropertiesTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_v2_invoice()

    def test_get_download_url(self):
        """it has get_download_url as a property"""
        assert self.test_get_download_url is not None
        import ipdb;ipdb.set_trace()

    def test_get_view_url(self):
        assert self.test_get_view_url is not None

class InvoiceMethodsTestCase(TestCase):

    def test_calculate_invoice_amount(self):

        invoice = Invoice()
        invoice.context = {
            "appointments": [
                {"price": 100},
                {"price": 200},
                {"price": 300},
            ]
        }
        invoice_amount = invoice.calculate_invoice_amount()
        assert invoice_amount == Decimal(600)

    def test_calculate_amount_paid(self):
        invoice = create_mock_v2_invoice()

        t1 = Transaction.from_invoice(invoice, transaction_type='Payment', amount=100, auto_created=False, with_save=True)
        t2 = Transaction.from_invoice(invoice, transaction_type='Payment', amount="10.45", auto_created=False, with_save=True)

        self.assertEqual(invoice.calculated_amount_paid, Decimal("110.45"))
