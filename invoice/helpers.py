from django.conf import settings
from dateutil.parser import parse
import requests

class Person:

    def __init__(self, person):
        '''
{
    "id": 95,
    "first_name": "Christo",
    "last_name": "Crampton",
    "id_number": "8209195149082",
    "password_number": null,
    "home_phone": "",
    "work_phone": "",
    "cell_phone": "+27832566533",
    "email": "christo@appointmentguru.co",
    "home_language": "English",
    "marital_status": "Married",
    "gender": "M",
    "home_address": "64 2nd avenue, Parkhurst",
    "work_address": "64 2nd avenue, Parkhurst",
    "postal_address": "64 2nd avenue, Parkhurst",
    "employer": "AppointmentGuru",
    "notes": "",
    "date_of_birth": "1982-09-19"
}
        '''
        self.person = person

    def _(self, key, default=''):
        return self.person.get(key, default)

    def fullname(self):
        return '{} {}'.format(self._('first_name'), self._('last_name'))

    def person_to_string(self):

        full_name = self.fullname()
        address = self._('home_address', self._('postal_address', self._('work_address')))
        contact = 'E-mail: {}\nMobile: {}'.format(self._('email'), self._('cell_phone'))
        return '{}\n{}\n{}'.format(full_name, address, contact)

def codes_to_table(codes):
    # this can be better!
    headers = []
    data = []
    ignored_fields = ['price', 'id', 'appointment', 'description', 'currency', 'price']
    for code_row in codes:
        for key, value in code_row.items():
            if key not in ignored_fields and value is not None                :
                if key not in headers: headers.append(key)

    for code_row in codes:
        row = []
        for field in headers:
            row.append(code_row[field])
        row.append('{}{}'.format(code_row['currency'], code_row['price']))
        data.append(row)

    headers.append('price')
    return {
        "headers": headers,
        "data": data
    }

def practitioner_details(p):
    pro = p.get('profile', {})
    name = '{} {}'.format(p.get('first_name', ''), p.get('last_name', ''))
    practice = pro.get('practice', None)
    practice_no = pro.get('practice_number', None)
    address = pro.get('billing_address', None)
    lines = [name]
    if practice is not None: lines.append(practice)
    if practice is not None: 'Practice #: {}'.format(lines.append(practice_no))
    if address is not None: lines.append(address)
    return ('\n').join(lines)

def medical_aid(data):
    fields = ['name', 'scheme', 'number']
    fullname = '{} {}'.format(
        data.get('first_name', ''),
        data.get('last_name', ''))
    lines = [fullname]

    for field in fields:
        value = data.get(field, '')
        line = '{}: {}'.format(field, value)
        lines.append(line)

    return ('\n').join(lines)

def fetch_data(practitioner_id, appointment_ids, client_id):
    headers = {
        'X_ANONYMOUS_CONSUMER': 'false',
        'X_AUTHENTICATED_USERID': str(practitioner_id),
    }

    # getme:
    url = '{}/api/practitioners/{}/'.format(settings.APPOINTMENTGURU_API, practitioner_id)
    practitioner = requests.get(url, headers=headers).json()

    appointments = []
    for appointment_id in appointment_ids:
        url = '{}/api/appointments/{}/'.format(settings.APPOINTMENTGURU_API, appointment_id)
        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            appointments.append(result.json())

    url = '{}/records/{}'.format(settings.MEDICALAIDGURU_API, client_id)
    record_request = requests.get(url, headers=headers)
    medical_record = {}
    if record_request.status_code == 200:
        medical_record = record_request.json()

    return (practitioner, appointments, medical_record)

def to_context(practitioner={}, appointments={}, medical_record={}):
    '''
    Given the above objects, create an invoice context json obj
    '''

    patient_info = Person(medical_record.get('patient', None)).person_to_string()
    account_info = Person(medical_record.get('account_person', None)).person_to_string()
    from_string = practitioner_details(practitioner)
    p = practitioner.get('profile', {})

    total = 0
    codes = [{
        "id": 33,
        "icd10": "M2.5",
        "procedure": None,
        "process": "2010",
        "currency": "ZAR",
        "nappi": None,
        "description": None,
        "price": "123.00",
        "appointment": 9863
    }, {
        "id": 32,
        "icd10": "M2.4",
        "procedure": None,
        "process": "4567",
        "currency": "ZAR",
        "nappi": None,
        "description": None,
        "price": "123.00",
        "appointment": 9863
    }, {
        "id": 31,
        "icd10": "M2.4",
        "procedure": None,
        "process": "1234",
        "currency": "ZAR",
        "nappi": None,
        "description": None,
        "price": "123.00",
        "appointment": 9863
    }]
    for appointment in appointments:
        total += float(appointment.get('price'))
        appointment.update({
            'codes': codes_to_table(codes),
            'start_time_formatted': parse(appointment.get('start_time'))
        })



    return {
        "notes": "",
        "from_string": from_string,
        "practice_name": p.get('practice_name'),
        "practice_number": p.get('practice_number'),
        "invoice_date": "2017-10-09",
        "patient_info": patient_info,
        "account_info": account_info,
        "customer_info": patient_info,
        "invoice_total": 0,
        "invoice_number": "2017-10-09-4825",
        "banking_details": p.get('banking_details', ''),
        "medicalaid_info": medical_aid(medical_record.get('medical_aid', {})),
        "practitioner_id": practitioner.get('id'),
        "due_date": "2017-10-09",
        "appointments": appointments
    }


'''

{
    "notes": "",
    "due_date": "2017-10-09",
    "total_due": 0,
    "total_paid": 0,
    "customer_id": 678,
    "from_string": "Christo Crampton\nE-mail: christo@appointmentguru.co\nPhone: +27832566533\n",
    "appointments": [{
        "id": 9782,
        "end": "18:00",
        "notes": null,
        "price": "4000.00",
        "start": "08:00",
        "title": "Luana Jordaan",
        "client": 678,
        "status": "N",
        "product": 88,
        "currency": "ZAR",
        "end_time": "2017-10-02T16:00:00Z",
        "included": true,
        "full_name": "Luana Jordaan",
        "start_time": "2017-10-02T06:00:00Z",
        "practitioner": 1,
        "invoice_description": null
    }, {
        "id": 9952,
        "end": "17:00",
        "hour": 8,
        "notes": null,
        "price": "4000.00",
        "start": "08:00",
        "title": "Luana Jordaan",
        "client": 678,
        "status": "N",
        "styles": {
            "top": "120px",
            "height": "540px"
        },
        "endHour": 17,
        "product": 88,
        "currency": "ZAR",
        "end_time": "2017-10-10T15:00:00Z",
        "included": true,
        "full_name": "Luana Jordaan",
        "start_time": "2017-10-10T06:00:00Z",
        "practitioner": 1,
        "exactOverlapCount": 1,
        "invoice_description": null,
        "exactOverlapSequence": 0
    }],
    "invoice_date": "2017-10-09",
    "paid_in_full": false,
    "patient_info": "",
    "customer_info": "Luana Jordaan",
    "invoice_total": 0,
    "invoice_number": "2017-10-09-4825",
    "banking_details": null,
    "medicalaid_info": "",
    "practitioner_id": 1
}
'''


