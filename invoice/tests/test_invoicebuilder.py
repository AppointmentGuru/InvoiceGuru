# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase, override_settings
from invoice.models import Invoice
from ..invoicebuilder import InvoiceBuilder

import responses

class InvoiceBuilderEnrichesContextTestCase(TestCase):

    @override_settings(APPOINTMENTGURU_API='http://appointmentguru')
    @override_settings(MEDICALAIDGURU_API='http://medicalaidguru')
    @responses.activate
    def setUp(self):
        self.invoice = Invoice()
        self.invoice.customer_id = 1
        self.invoice.practitioner_id = 2
        self.invoice.appointments = [3,4,5]

        practitioner_data = {
            'id': 2,
            'username': 'jane@soap.com',
        }

        responses.add(
            responses.GET,
            'http://appointmentguru/api/users/1/',
            json={
                'id': 1,
                'first_name': 'Joe'},
            status=200
        )
        responses.add(
            responses.GET,
            'http://appointmentguru/api/practitioners/2/',
            json=practitioner_data,
            status=200
        )
        responses.add(
            responses.GET,
            'http://medicalaidguru/records/1/',
            json={
                'customer_id': '1',
                'practitioners': ['2'],
                'patient': {
                    'first_name': 'Joe'
                }
            },
            status=200
        )
        for x in [3,4,5]:
            responses.add(
                responses.GET,
                'http://appointmentguru/api/appointments/{}/'.format(x),
                json={
                    'process': { },
                    'practitioner': { "id": 2},
                    'start_time': "2018-07-08T14:05:49.594+02:00",
                    'end_time': "2018-07-08T14:35:49.594+02:00"
                },
                status=200
            )

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

