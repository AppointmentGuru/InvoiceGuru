'''
Tests for helpers.py
'''
from django.test import TestCase
from ..helpers import get_appointments_in_range, prepare_appointments_for_construction
import responses

from .responses import APPOINTMENTS_LIST

class GetAppointmentsTestCase(TestCase):

    @responses.activate
    def test_get_appointments_in_range(self):
        responses.add(
            responses.GET,
            url='http://appointmentguru/api/appointments/?after_utc=2017-06-01&before_utc=2017-06-30',
            json=APPOINTMENTS_LIST,
            status=200
        )
        appts = get_appointments_in_range(1, '2017-06-01', '2017-06-30')
        assert len(appts) == len(APPOINTMENTS_LIST)

class PrepareAppointmentsTestCase(TestCase):

    def test_groups_by_clients(self):
        prepare_appointments_for_construction(APPOINTMENTS_LIST)

