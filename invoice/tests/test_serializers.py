# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from ..serializers import TransactionSerializer
from ..models import Payment

from api.testutils import (
    create_mock_invoice
)


class TransactionSerializerTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    def test_seriailizes_invoice(self):
        transaction = TransactionSerializer.from_invoice(self.invoice)
        print(transaction.data)

    def test_serializes_payment(self):
        self.invoice.amount_paid = self.invoice.invoice_amount
        payment = Payment.from_invoice(self.invoice)
        transaction = TransactionSerializer.from_payment(payment)
        print(transaction.data)