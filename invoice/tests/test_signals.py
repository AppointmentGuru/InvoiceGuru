# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase
from api.testutils import create_mock_v2_invoice
from decimal import Decimal

import unittest

class InvoicePreSaveTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_v2_invoice()

    def test_it_sets_fields_from_context(self):
        pass

    def test_it_sets_from_to_based_on_appointments_if_not_already_set(self):
        pass

    def test_it_doesnt_set_from_to_if_already_set(self):
        pass

    def test_it_adds_appointment_to_object_ids(self):
        pass

    def test_it_doesnt_add_appointment_to_object_ids_if_already_exists(self):
        pass

    def test_it_handles_if_there_are_no_appointments_set(self):
        pass

class PostSaveInvoiceTestCase(TestCase):

    def setUp(self):
        appointments = {
            3: {"price": 100},
            4: {"price": 200},
            5: {"price": 300},
        }
        extra = { "appointments": appointments }
        self.invoice = create_mock_v2_invoice(
            appointments=[3,4,5],
            extra_data=extra
        )

    def test_it_calculates_invoice_total(self):
        self.assertEqual(self.invoice.invoice_amount, Decimal(600))

    def test_it_creates_an_invoice_transaction_for_sent_invoices(self):
        data = { "status": "sent" }
        invoice = create_mock_v2_invoice(
            invoice_data = data
        )
        invoice_transaction = self.invoice.transaction_set.first()
        self.assertEqual(self.invoice.transaction_set.count(), 1)
        self.assertEqual(invoice_transaction.type, 'Invoice')
        self.assertEqual(self.invoice.invoice_amount, invoice_transaction.amount)

    def test_it_creates_an_invoice_and_payment_transaction_for_paid_invoices(self):
        data = { "status": "paid" }
        invoice = create_mock_v2_invoice(invoice_data=data)
        invoice_transaction = invoice.transaction_set.first()
        payment_transaction = invoice.transaction_set.filter(type='Payment').first()

        self.assertEqual(invoice.transaction_set.count(), 2)
        self.assertEqual(invoice_transaction.amount, payment_transaction.amount)
        self.assertEqual(invoice.invoice_total, invoice.calculated_amount_paid)
