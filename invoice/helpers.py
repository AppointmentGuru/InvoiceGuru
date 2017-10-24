from django.conf import settings
from dateutil.parser import parse
import requests


def get_headers(practitioner_id):
    return {
        'X_ANONYMOUS_CONSUMER': 'false',
        'X_AUTHENTICATED_USERID': str(practitioner_id),
    }

class Person:

    def __init__(self, person):
        self.person = person

    def _(self, key, default=''):
        return self.person.get(key, default)

    def fullname(self):
        return '{} {}'.format(self._('first_name'), self._('last_name'))

    def person_to_string(self):
        if self.person is None: return ''
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

def fetch_appointments(practitioner_id, appointment_ids):
    headers = get_headers(practitioner_id)
    appointments = []
    for appointment_id in appointment_ids:
        url = '{}/api/appointments/{}/'.format(settings.APPOINTMENTGURU_API, appointment_id)
        result = requests.get(url, headers=headers)
        if result.status_code == 200:
            appointments.append(result.json())
    return appointments

def fetch_data(practitioner_id, appointment_ids, client_id):
    # getme:
    headers = get_headers(practitioner_id)
    url = '{}/api/practitioners/{}/'.format(settings.APPOINTMENTGURU_API, practitioner_id)
    practitioner = requests.get(url, headers=headers).json()

    appointments = fetch_appointments(practitioner_id, appointment_ids)

    url = '{}/records/{}'.format(settings.MEDICALAIDGURU_API, client_id)
    record_request = requests.get(url, headers=headers)
    medical_record = {}
    if record_request.status_code == 200:
        medical_record = record_request.json()

    return (practitioner, appointments, medical_record)

def to_context(practitioner={}, appointments={}, medical_record={}, default_context={}, format_times = True):
    '''
    Given the above objects, create an invoice context json obj
    '''

    patient_info = Person(medical_record.get('patient', None)).person_to_string()
    account_info = Person(medical_record.get('account_person', None)).person_to_string()
    from_string = practitioner_details(practitioner)
    p = practitioner.get('profile', {})

    total = 0
    for appointment in appointments:
        total += float(appointment.get('price'))
        codes = appointment.get('codes', [])
        appointment.update({
            'codes': codes_to_table(codes),
        })
        if format_times:
            appointment.update({
                'start_time_formatted': parse(appointment.get('start_time'))
            })

    default_context.update({
        "notes": "",
        "from_string": from_string,
        "practice_name": p.get('practice_name'),
        "practice_number": p.get('practice_number'),
        "patient_info": patient_info,
        "account_info": account_info,
        "customer_info": patient_info,
        "invoice_total": 0,
        "banking_details": p.get('banking_details', ''),
        "medicalaid_info": medical_aid(medical_record.get('medical_aid', {})),
        "practitioner_id": practitioner.get('id'),
        "appointments": appointments
    })
    return default_context


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


