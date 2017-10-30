# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase
from api.testutils import create_mock_invoice

class InvoicePreSaveTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    def test_it_sets_fields_from_context(self):
        pass

    def test_it_sets_from_to_based_on_appointments_if_not_already_set(self):
        pass

    def test_it_doesnt_set_from_to_if_already_set(self):
        pass

    def test_it_calculates_total(self):
        pass

    def test_it_adds_appointment_to_object_ids(self):
        pass

    def test_it_doesnt_add_appointment_to_object_ids_if_already_exists(self):
        pass

    def test_it_handles_if_there_are_no_appointments_set(self):
        pass