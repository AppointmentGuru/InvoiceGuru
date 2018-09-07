import responses
from django.conf import settings
from decimal import Decimal

from faker import Factory
FAKE = Factory.create()

MESSAGE_SUCCESS_RESPONSE = {
	"id": 60,
	"owner": "836",
	"object_ids": ["user:836", "user:930", "appointment:8148", "appointment:8147", "appointment:8149", "appointment:8150"],
	"sender_email": "support@appointmentguru.co",
	"preferred_transport": "email",
	"recipient_channel": None,
	"recipient_id": None,
	"recipient_emails": ["info@38.co.za"],
	"recipient_phone_number": None,
	"subject": "Your invoice for 2017-09-14",
	"short_message": None,
	"message": "Hi\\n\\nAttached please find your invoice for 2017-09-14.\\nYou can also view it online at:\\nhttps://google.com",
	"attached_urls": ["https://google.com"],
	"context": None,
	"send_date": "2017-11-10T13:21:32.339320",
	"last_sent_date": None,
	"status": "N",
	"created_date": "2017-11-10T13:21:32.363299Z",
	"modified_date": "2017-11-10T13:21:33.718522Z",
	"backend_used": "anymail.backends.mailgun.MailgunBackend",
	"backend_message_id": "<20171110132133.111041.275C5155A4455F96@appointmentguru.co>",
	"backend_result": {
		"id": "<20171110132133.111041.275C5155A4455F96@appointmentguru.co>",
		"message": "Queued. Thank you."
	},
	"template": None
}

def get_call(calls, search):
    for call in calls:
    		if search in call.request.url:
    			return call

def get_responses(responses_mock=None):
	'''
	rsps = get_responses(responses_mock)
	'''
	rsps = responses
	if responses_mock is not None:
		rsps = responses_mock
	return rsps

def expect_shorten_url():
	url = "https://www.googleapis.com/urlshortener/v1/url"
	responses.add(
		responses.POST,
		url=url,
		json={'id': 'https://go.gle/1234'}
	)

def expect_keen_response():
	keen_url = 'https://api.keen.io/3.0/projects/{}/events/snapscan_webhook'.format(settings.KEEN_PROJECT_ID)
	responses.add(
		responses.POST,
		url=keen_url,
		json={'ok': 'true'}
	)

def expect_communications_response(response_data={}, responses_mock = None):
	rsps = get_responses(responses_mock)

	data = {"id": 1}
	data.update(response_data)
	base = settings.COMMUNICATIONGURU_API
	url = "{}/communications/".format(base)

	rsps.add(
		responses.POST,
		url=url,
		json=data,
		status=201
	)

def expect_get_user_response(user_id, response_data={}, responses_mock = None):
	rsps = get_responses(responses_mock)
	data = {
		'id': user_id,
		'first_name': 'Joe'
	}
	if response_data is not None:
		data.update(response_data)
	rsps.add(
		responses.GET,
		'{}/api/v2/practitioner/clients/{}/'.format(settings.APPOINTMENTGURU_API, user_id),
		json=data,
		status=200
	)
def expect_get_practitioner_response(practitioner_id, responses_mock = None):
	rsps = get_responses(responses_mock)

	practitioner_data = {
		'id': practitioner_id,
		'username': 'jane@soap.com',
		"profile": {}
	}
	rsps.add(
		responses.GET,
		'{}/api/practitioners/{}/'.format(settings.APPOINTMENTGURU_API, practitioner_id),
		json=practitioner_data,
		status=200
	)

def record_response_data(customer_id, practitioner_id, response_data = {}):

	data = {
		'customer_id': customer_id,
		'practitioners': [practitioner_id],
		'patient': {
			'first_name': 'Joe'
		}
	}
	data.update(response_data)
	return data

def expect_patch_record_response(customer_id, practitioner_id, response_data = {}, responses_mock=None):
	rsps = get_responses(responses_mock)
	data = record_response_data(customer_id, practitioner_id, response_data)
	url = '{}/records/{}/'.format(settings.MEDICALAIDGURU_API, customer_id)
	rsps.add(responses.PATCH, url, json=data)

def expect_get_record_response(customer_id, practitioner_id, response_data = {}, responses_mock = None):
	rsps = get_responses(responses_mock)
	data = record_response_data(customer_id, practitioner_id, response_data)
	url = '{}/records/{}/'.format(settings.MEDICALAIDGURU_API, customer_id)
	rsps.add(responses.GET, url, json=data)

def expect_get_appointment(appointment_id, practitioner_id, response_data={}, responses_mock = None):
	rsps = get_responses(responses_mock)
	data = {
		'process': { },
		'id': appointment_id,
		'practitioner': { "id": practitioner_id },
		'client': { "id": 123 },
		'start_time': "2018-07-08T14:05:49.594+02:00",
		'end_time': "2018-07-08T14:35:49.594+02:00",
		'price': FAKE.pyint()
	}
	data.update(response_data)
	url = '{}/api/appointments/{}/'.format(
		settings.APPOINTMENTGURU_API,
		appointment_id
	)
	rsps.add(
		responses.GET,
		url,
		json = data,
		status = 200
	)

def expect_get_appointments(appointment_ids, practitioner_id, response_data={}, responses_mock = None):

	extra_data = response_data.get('appointments', {})

	for x in appointment_ids:
		data = extra_data.get(x, {})
		expect_get_appointment(
			appointment_id=x,
			practitioner_id = practitioner_id,
			response_data=data,
			responses_mock=responses_mock
		)

