from django.test import TestCase
from django.urls import reverse

from api.testutils import create_mock_invoice, create_mock_user, get_proxy_headers
from ..models import Invoice

import responses, json

class InvoiceAppointmentsTestCase(TestCase):

    @responses.activate
    def setUp(self):
        responses.add(
            responses.GET,
            'http://appointmentguru/api/appointments/1/',
            json={'id': '1'},
            status=200)
        responses.add(
            responses.GET,
            'http://appointmentguru/api/appointments/2/',
            json={'id': '2'},
            status=200)
        responses.add(
            responses.GET,
            'http://appointmentguru/api/appointments/3/',
            json={'id': '3'},
            status=200)

        invoice = create_mock_invoice()
        self.url = reverse('invoice-appointments', args=(invoice.pk,))
        headers = get_proxy_headers(invoice.practitioner_id)
        data = {
            'appointments': '1,2,3'
        }
        self.response = self.client.post(self.url, json.dumps(data), content_type='application/json', **headers)

    def test_is_ok(self):
        assert self.response.status_code == 200

    def test_result_contants_appointment_response(self):
        appointments = self.response.json().get('context').get('appointments')
        for index, id in enumerate(["1","2","3"]):
            actual = appointments[index].get('id')
            assert actual == id,\
                'Expected: {}. Got: {}'.format(id, actual)

    def test_only_practitioner_can_access(self):
        user = create_mock_user('joe')
        invoice = create_mock_invoice()
        url = reverse('invoice-appointments', args=(invoice.pk,))
        headers = get_proxy_headers(user.id)
        response = self.client.post(url, json.dumps({}), content_type='application/json', **headers)
        assert response.status_code == 404

class ApiInvoiceListTestCase(TestCase):

    def setUp(self):
        user_1 = create_mock_user('joe')
        user_2 = create_mock_user('jane')

        create_mock_invoice(user_1.id)
        create_mock_invoice(user_1.id)
        create_mock_invoice(user_1.id, user_2.id)

        create_mock_invoice(user_2.id)
        create_mock_invoice(user_2.id)
        create_mock_invoice(user_2.id)

        self.user_2 = user_2

        self.url = reverse('invoice-list')
        headers = get_proxy_headers(user_1.id)
        self.response = self.client.get(self.url, **headers)

    def test_is_ok(self):
        assert self.response.status_code == 200, \
            'Expected 200. got: {} {}'.format(
                self.response.status_code,
                self.response.context)

    def test_only_get_own_invoices(self):
        assert self.response.json().get('count') == 3

    def test_also_gets_invoices_where_im_a_consumer(self):
        url = reverse('invoice-list')
        headers = get_proxy_headers(self.user_2.id)
        response = self.client.get(url, **headers)
        num_invoices = response.json().get('count')
        assert num_invoices == 4, \
            'Expected 4. got: {}'.format(num_invoices)
