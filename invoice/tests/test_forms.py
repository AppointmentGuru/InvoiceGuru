# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase

from ..forms import InvoiceConstructionForm, UpdateInvoiceDetailsForm
from api.testutils import create_mock_invoice

class InvoiceConstructionFormTestCase(TestCase):

    def setUp(self):
        self.form = InvoiceConstructionForm()

    def test_it_works(self):
        pass
        # if self.form.isValid():
        #     self.form.save()

class UpdateInvoiceDetailsFormTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()
        self.data = {
            'medicalaid': 'Discovery',
            'scheme': 'Classic Comprehensive',
            'number': '1234',
            'patient_first_name': 'Joe',
            'patient_last_name': 'Soap',
            'patient_id_number': '5678',
            'is_dependant': True,
            'member_first_name': 'Jane',
            'member_last_name': 'Soap',
            'member_id_number': '91011'
        }

    def test_save_valid_result(self):

        form = UpdateInvoiceDetailsForm(self.data)
        if form.is_valid():
            invoice = form.save(self.invoice)
            print(invoice.context.get('medicalaid_info'))


