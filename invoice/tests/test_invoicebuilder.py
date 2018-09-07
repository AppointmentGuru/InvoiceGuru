# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings
from invoice.models import Invoice, InvoiceSettings
from ..invoicebuilder import InvoiceBuilder
from api.testutils import create_mock_v2_invoice
import responses, unittest

from faker import Factory
FAKE = Factory.create()

class InvoiceBuilderEnrichesContextTestCase(TestCase):

    @override_settings(APPOINTMENTGURU_API='http://appointmentguru')
    @override_settings(MEDICALAIDGURU_API='http://medicalaidguru')
    def setUp(self):
        self.fields = [
            'practitioner_data',
            'client_data',
            'appointment_data',
            'record_data'
        ]
        self.invoice = create_mock_v2_invoice()
        self.builder = InvoiceBuilder(self.invoice)

        #self.context = self.builder.enrich(save_context=True)

    def test_it_sets_datas(self):

        for field in self.fields:
            assert getattr(self.invoice, field, None) is not None

    def test_it_sets_practitioner(self):
        practitioner = self.invoice.practitioner_data
        assert practitioner.get('id') == 2,\
            'Practitioner data is missing: {}'\
            .format(practitioner)

    def test_it_sets_client(self):
        assert self.invoice.client_data.get('id') == 1

    def test_it_sets_appointments(self):
        appointments = self.invoice.appointment_data
        num_appointments = len(appointments)
        self.assertEqual(num_appointments, 3)


class BuilderAppliesContext(TestCase):

    def __inv_and_builder(self):
        inv = Invoice()
        builder = InvoiceBuilder(inv)
        return (inv, builder)

    def test_set_customer_info_from_context_sets_invoicee_details_from_client_if_no_record(self):

        inv, builder = self.__inv_and_builder()
        inv.client_data = {
            "email": "jane@gmail.com",
            "last_name": "Jane",
            "first_name": "Soap",
            "phone_number": "+2781234567",
        }
        builder.set_customer_info(with_save=False)
        num_lines = len(inv.invoicee_details.split('\n'))
        self.assertEqual(num_lines, 3)

    def test_sets_invoice_details_from_client_record(self):
        inv, builder = self.__inv_and_builder()
        inv.record_data = {
            "patient": {
                "first_name": "Jake",
                "last_name": "White",
                "cell_phone": "+27821234567",
                "billing_address": "101 Infinite Loop",
            }
        }
        builder.set_customer_info(with_save=False)
        assert len(inv.invoicee_details.split('\n')) == 3,\
            'invoicee_details looks wrong: {}'.format(inv.invoicee_details)

    def test_sets_medicalaid_details_with_dependent(self):
        inv, builder = self.__inv_and_builder()
        inv.record_data = {
            "medical_aid": {
                "name": "DISCOVERY Health Medical Scheme",
                "number": "67890",
                "scheme": "Comprehensive",
                "is_dependent": True,
                "member_id_number": "123456",
                "member_last_name": "Joe",
                "member_first_name": "Soap",
                "patient_id_number": "82091951491234",
                "patient_last_name": "Jane",
                "patient_first_name": "Soap"
            }
        }
        builder.set_customer_info(with_save=False)
        assert len(inv.medicalaid_details.split('\n')) == 8,\
            'medicalaid_details (for dependant) looks wrong: {}'.format(inv.medicalaid_details)

    def test_sets_medicalaid_details_without_dependent(self):
        inv, builder = self.__inv_and_builder()
        inv.record_data = {
            "medical_aid": {
                "name": "DISCOVERY Health Medical Scheme",
                "number": "67890",
                "scheme": "Comprehensive",
                "is_dependent": False,
                "member_id_number": "123456",
                "member_last_name": "Joe",
                "member_first_name": "Soap",
                "patient_id_number": "82091951491234",
                "patient_last_name": "Jane",
                "patient_first_name": "Soap"
            }
        }
        builder.set_customer_info(with_save=False)
        assert len(inv.medicalaid_details.split('\n')) == 5,\
            'medicalaid_details (for main member) looks wrong: {}'.format(inv.medicalaid_details)

class BuilderAppliesSettingsTestCase(TestCase):
    """Verify settings will apply if nothing is set"""
    def setUp(self):
        self.p_id = 1
        settings = InvoiceSettings()
        settings.practitioner_id = self.p_id
        settings.integrate_medical_aid = True
        settings.billing_address = "Some address"
        settings.banking_details = "Bank of AppointmentGuru"
        settings.save()

        self.invoice = Invoice()
        self.settings = settings
        self.invoice.practitioner_id = self.p_id

        self.builder = InvoiceBuilder(self.invoice)
        self.builder.apply_settings(self.invoice, settings)

    def test_it_sets_medical_aid_details(self):
        assert self.invoice.integrate_medical_aid == True

    def test_it_sets_billing_address(self):
        self.assertEqual(
            self.invoice.billing_address,
            "Some address"
        )

    def test_it_sets_banking_details(self):
        self.assertEqual(
            self.invoice.banking_details,
            "Bank of AppointmentGuru"
        )

    def test_it_handles_an_empty_string(self):
        self.invoice.billing_address = ""
        self.builder.apply_settings(self.invoice, self.settings)
        self.assertEqual(
            self.invoice.billing_address,
            "Some address"
        )

class BuilderOverrideSettingsTestCase(TestCase):
    """Verify that settings don't override already set values"""

    def __test_settings(self, field, invoice_value, settings_value, expected_result):
        setattr(self.invoice, field, invoice_value)
        setattr(self.settings, field, invoice_value)

        self.builder.apply_settings(self.invoice, self.settings)

        assert getattr(self.invoice, field) == expected_result,\
            'Expected {} to be: {}. Settings were: {}. Invoice was: {}'.format(
                field,
                expected_result,
                settings_value,
                invoice_value
            )

    def setUp(self):
        self.settings = InvoiceSettings()
        self.invoice = Invoice()
        self.builder = InvoiceBuilder(self.invoice)

    def test_it_doesnt_override_integrate_medical_aid_if_exists(self):
        self.__test_settings(
            'integrate_medical_aid',
            invoice_value=False,
            settings_value=True,
            expected_result=False
        )

    def test_it_doesnt_override_billing_address_if_exists(self):
        self.__test_settings(
            'billing_address',
            invoice_value="invoice address",
            settings_value="settings address",
            expected_result="invoice address"
        )

