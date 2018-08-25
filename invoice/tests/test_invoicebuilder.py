# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings
from invoice.models import Invoice
from ..invoicebuilder import InvoiceBuilder
from api.testutils import create_mock_v2_invoice
import responses

from faker import Factory
FAKE = Factory.create()

class InvoiceBuilderEnrichesContextTestCase(TestCase):

    @override_settings(APPOINTMENTGURU_API='http://appointmentguru')
    @override_settings(MEDICALAIDGURU_API='http://medicalaidguru')
    @responses.activate
    def setUp(self):

        self.invoice = create_mock_v2_invoice()

        self.builder = InvoiceBuilder(self.invoice)
        self.context = self.builder.enrich(save_context=True)

    def test_build_context(self):
        assert self.invoice.context is not None

    def test_it_sets_practitioner(self):
        assert self.invoice.context.get('practitioner').get('id') == 2,\
            'Practitioner data is missing: {}'.format(
                self.invoice.context.get('practitioner')
            )

    def test_it_sets_client(self):
        assert self.invoice.context.get('client').get('id') == 1

    def test_it_sets_appointments(self):
        appointments = self.invoice.context.get('appointments', [])
        num_appointments = len(appointments)
        assert num_appointments == 3,\
            'Expected 3 appointments. Got: {}. {}'.format(num_appointments, appointments)

    def test_it_formats_a_billing_address(self):
        data = {
            "profile": {
                "services": [
                    {"address": {
                        "name": "Downtown Abby",
                        "address": "10 Downtown Abbey, England"
                    }}
                ]
            }
        }
        result = self.builder.get_billing_address(data)
        self.assertEquals(result, 'Downtown Abby\n10 Downtown Abbey, England\n')

class BuilderSetsContext(TestCase):

    def __inv_and_builder(self):
        inv = Invoice()
        builder = InvoiceBuilder(inv)
        return (inv, builder)

    def test_set_customer_info_from_context_sets_invoicee_details_from_client_if_no_record(self):

        inv, builder = self.__inv_and_builder()
        inv.context = {
            "client": {
                "email": "jane@gmail.com",
                "last_name": "Jane",
                "first_name": "Soap",
                "phone_number": "+2781234567",
            },
            "record": {}
        }
        builder.set_customer_info_from_context(with_save=False)
        assert inv.invoicee_details == 'Soap Jane\nemail: jane@gmail.com\ncontact: +2781234567'

    def test_sets_invoice_details_from_client_record(self):
        inv, builder = self.__inv_and_builder()
        inv.context = {
            "record": {
                "patient": {
                    "first_name": "Jake",
                    "last_name": "White",
                    "cell_phone": "+27821234567",
                    "home_address": "101 Infinite Loop",
                },
            }
        }
        builder.set_customer_info_from_context(with_save=False)
        assert inv.invoicee_details == 'Jake White\nemail: None\ncontact: +27821234567\n101 Infinite Loop'

    def test_sets_medicalaid_details(self):
        inv, builder = self.__inv_and_builder()
        inv.context = {
            "record": {
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
        }
        builder.set_customer_info_from_context(with_save=False)
        assert inv.medicalaid_details == 'DISCOVERY Health Medical Scheme. Comprehensive\n#67890.\nPatient:\nSoap Jane\nID: 82091951491234\nMain member:\nSoap Joe\nID: 123456'

