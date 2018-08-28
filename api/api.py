from django.conf import settings
import requests, responses

API = {
    "appointmentguru": {
        "base_url": settings.APPOINTMENTGURU_API,
        "resources": {
            "appointment": {
                "path": "api/appointments/"
            },
            "practitioner": {
                "path": "api/practitioners/"
            },
            "user": {
                "path": "api/users/"
            }
        }
    },
    "medicalaidguru": {
        "base_url": settings.MEDICALAIDGURU_API,
        "resources": {
            "record": {
                "path": "records/"
            }
        }
    },
    "communicationguru": {
        "base_url": settings.APPOINTMENTGURU_API,
        "resources": {
        }
    }
}

def get_micro(service, practitioner_id):
    """
    micro = get_micro("appointmentguru", 1)
    """
    headers = {
        'X_ANONYMOUS_CONSUMER': 'False',
        'X_AUTHENTICATED_USERID': str(practitioner_id),
        'X_CONSUMER_USERNAME': "invoiceguru",
    }
    return Micro(API, service, headers = headers)

class Micro:
    '''
    usage: response, data, is_ok = Micro(API, 'appointmentguru').list('appointment', default={})
    usage: response, data, is_ok = Micro(API, 'appointmentguru').get('appointment', id, default={})
    '''

    def __init__(self, api_definition, service_name, headers={}):
        self.defn = api_definition
        self.service = service_name
        self.headers = headers

    def _prepare_request(self, resource_name, id = None):
        defn = self.defn.get(self.service)
        base_url = defn.get('base_url')
        path = defn.get('resources', {}).get(resource_name).get('path')
        if id is not None:
            path = "{}{}/".format(path, id)

        return "{}/{}".format(base_url, path)

    def __make_request(self, url, params=None, extra_headers={}):
        headers = self.headers.copy()
        headers.update(extra_headers)
        data = {
            "headers": headers
        }
        return requests.get(url, **data)

    def __get_response_data(self, response, default_response={}):
        if response.ok:
            return response.json()
        else:
            return default_response

    def list(self, resource, params=None, extra_headers={}, default_response={}):
        url = self._prepare_request(resource)
        response = self.__make_request(url, params, extra_headers)
        data = self.__get_response_data(response)
        return (response, data, response.ok)

    def get(self, resource, id, params=None, extra_headers={}, default_response={}):
        url = self._prepare_request(resource, id)
        response = self.__make_request(url, params, extra_headers)
        data = self.__get_response_data(response)
        return (response, data, response.ok)


class MockMicro:

    def __init__(self, micro):
        self.micro = micro

    def expect(self, resource, id=None, response_data={}, response_status=200):
        url = self.micro._prepare_request(resource, id)
        print(url)
        responses.add(
            responses.GET,
            url,
            json=response_data,
            status=response_status
        )

