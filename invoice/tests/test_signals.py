# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase
from api.testutils import create_mock_invoice
import unittest 

class InvoicePreSaveTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    def test_it_sets_fields_from_context(self):
        pass

    @unittest.skip('revisit later')
    def test_lineitem_price_overrides_appointment_price(self):
        assert self.invoice.context.get('appointments')[0].get('price') == '650.00',\
            'Expect price to have been set to the lineitem cost'

    def test_use_default_price_if_no_codes_specified(self):
        # assert self.invoice.context.get('appointments')[1].get('codes', []) == 0
        price = self.invoice.context.get('appointments')[1].get('price')
        assert price == '326.00', \
            'Expect price to be default prioce if no codes on appointment. Expected 326.00. Got: {}'.format(price)

    def test_it_sets_from_to_based_on_appointments_if_not_already_set(self):
        pass

    def test_it_doesnt_set_from_to_if_already_set(self):
        pass

    @unittest.skip('revisit later')
    def test_it_calculates_total(self):
        print (self.invoice.invoice_amount)
        assert self.invoice.invoice_amount == 1952,\
            'Expected 1952. Got: {}'.format(self.invoice.invoice_amount)

    def test_it_adds_appointment_to_object_ids(self):
        pass

    def test_it_doesnt_add_appointment_to_object_ids_if_already_exists(self):
        pass

    def test_it_handles_if_there_are_no_appointments_set(self):
        pass