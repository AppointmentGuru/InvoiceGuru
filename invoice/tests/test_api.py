from django.test import TestCase
from api.testutils import create_mock_invoice
from ..models import Invoice

class ApiRootTestCase(TestCase):

    def test_get_html_root(self):
        response = self.client.get('/', **{'HTTP_ACCEPT':'text/html'})
        assert response.status_code == 200

    def test_get_html_root_logged_in_via_upstream(self):
        headers = {
            'HTTP_ACCEPT': 'text/html',
            'HTTP_X_ANONYMOUS_CONSUMER': 'false',
            'HTTP_X_AUTHENTICATED_USERID': '1'
        }
        response = self.client.get('/', **headers)
        assert response.status_code == 200