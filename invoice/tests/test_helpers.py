# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from api.testutils import (
    create_mock_invoice
)
from invoice.helpers import (
    clean_object,
    clean_context,
    get_invoice_template
)
from .datas import (
    example_context
)

class GetInvoiceTemplateTestCase(TestCase):

    def setUp(self):
        self.invoice = create_mock_invoice()

    def test_no_details_requested(self):
        result = get_invoice_template(self.invoice)
        assert result == 'view'

    def test_medical_aid_details_required(self):
        self.invoice.request_medical_aid_details = True
        possible_empty_values = [None, "", "{}"]
        for val in possible_empty_values:
            self.invoice.context.update({
                "medicalaid_info": val
            })
            result = get_invoice_template(self.invoice)
            assert result == 'edit'

    def test_medical_aid_details_already_exist(self):
        self.invoice.request_medical_aid_details = True
        self.invoice.context.update({
            "medicalaid_info": "Joe Soap. Disovery"
        })
        result = get_invoice_template(self.invoice)
        assert result == 'view'


class CleanContextTestCase(TestCase):

    def setUp(self):
        self.context = example_context

    def test_clean_object(self):

        obj = {
            "foo": "foo",
            "bar": "bar",
            "baz": "baz"
        }
        remove_fields = ["foo", "baz"]
        clean_object(obj, remove_fields)
        for field in remove_fields:
            assert obj.get(field) is None

    def test_cleans_client(self):

        client = {
			'id': 678,
			'email': 'luana.jordaan@gmail.com',
			'title': None,
			'initials': None,
			'is_admin': False,
			'is_active': True,
			'last_name': 'Jordaan',
			'first_name': 'Luana',
			'last_login': '2017-04-28T09:36:18.419314Z',
			'date_joined': '2017-04-28T09:36:18.419204Z',
			'phone_number': '+27823201039',
			'email_confirmed': False,
			'is_practitioner': False,
			'phone_number_confirmed': False
		}
        context = { "client": client }
        clean_context(context)

    def test_handles_practitioner_is_int(self):
        context = {
            'appointments': [
                {
                    'practitioner': 1
                }
            ]
        }

    def test_clean_practitioner_profile(self):

        context = {
            'appointments': [
                {
                    'practitioner': {
                        'profile': {
                            'data': {},
                            'slug': 'guru',
                            'tags': None,
                            'user': 1,
                            'twitter': '',
                            'business': [],
                            'currency': 'ZAR',
                            'facebook': 'https://www.facebook.com/appointmentguru/',
                            'linkedin': '',
                            'timezone': 'Africa/Johannesburg',
                            'instagram': '',
                            'published': True,
                            'profession': {
                                'id': 2,
                                'name': 'AppointmentGuru Consultant'
                            },
                            'sub_domain': 'guru',
                            'clients_url': '/api/v2/practitioner/clients/',
                            'description': 'Interested in learning more about [AppointmentGuru](http://appointmentguru.co)? We do demos in the Johannesburg area. You can book an appointment below.',
                            'logo_picture': 'https://media-appointmentguru.s3.amazonaws.com:443/practitioner/images/1/logo.png',
                            'practice_name': '',
                            'banking_details': 'Christopher Crampton. \r\nFNB. \r\nAccount number: 60232195566',
                            'is_test_account': False,
                            'practice_number': '',
                            'profile_picture': 'https://media-appointmentguru.s3.amazonaws.com:443/practitioner/images/1/profile.jpg',
                            'is_visible_in_app': True,
                            'background_picture': '//images.unsplash.com/photo-1453928582365-b6ad33cbcf64?ixlib=rb-0.3.5&q=80&fm=jpg&crop=entropy&cs=tinysrgb&w=1080&fit=max&ixid=eyJhcHBfaWQiOjExOTkxfQ&s=91d6ef7d248f9bbb73bb41cd1e0ce248',
                            'is_website_published': True,
                            'free_trial_expiry_date': None
                        }
                    }
                }
            ]
        }
        clean_context(context)
        print(context)