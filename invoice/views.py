from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from functools import reduce
from datetime import datetime
from dateutil.parser import parse

import requests, decimal, random, json

DEFAULT_CONTEXT = {
    "invoice_number": "# LJ-20170825-374",
    "from_string": "Christo Crampton\n64 2nd ave, \nParkhurst \nJohannesburg",
    "customer_info": "Vumatel (Pty) Ltd\nVAT reg: 4020266740 \nAddress: PO Box 1811 \nParklands\n2121",
    "invoice_date": "2017-08-25",
    "due_date": "2017-08-25",
    "notes": "**Banking details:**\nChristo Crampton\nFNB\nAcc no: 60232195566\nBranch code: 252505",
    "invoice_total": 8000,
    "total_due": 8000,
    "total_paid": 0,
    "paid_in_full": False,
    "appointments": [
        {
            "id": 8681,
            "start_time": "2017-08-15T07:00:00Z",
            "end_time": "2017-08-15T16:00:00Z",
            "title": "Luana Jordaan",
            "full_name": "Luana Jordaan",
            "client": 678,
            "practitioner": 1,
            "status": "N",
            "currency": "ZAR",
            "price": "4000.00",
            "product": 88,
            "notes": None,
            "invoice_description": None
        },
        {
            "id": 8868,
            "start_time": "2017-08-24T07:00:00Z",
            "end_time": "2017-08-24T15:05:00Z",
            "title": "Luana Jordaan",
            "full_name": "Luana Jordaan",
            "client": 678,
            "practitioner": 1,
            "status": "N",
            "currency": "ZAR",
            "price": "4000.00",
            "product": 88,
            "notes": None,
            "invoice_description": None
        }
    ]
}

@csrf_exempt
def invoice(request):

    context = {}

    try:
        context.update(json.loads(request.body))
    except json.decoder.JSONDecodeError:
        pass

    for appt in context.get('appointments', []):
        appt['start_time_formatted'] = parse(appt.get('start_time'))

    return render(request, 'invoice/templates/basic.html', context=context)

"""
    token = request.GET.get('token', None)
    client = request.GET.get('client')
    from_date = request.GET.get('from')
    to_date = request.GET.get('to')

    headers = {'content-type': 'application/json'}
    if token is not None:
        headers.update({
            "Authorization": "Token {}".format(token)
        })
    url = 'https://api.appointmentguru.co/api/appointments/?client={}&after_utc={}'.format(client, from_date)
    print(url)
    result = requests.get(url, headers=headers)
    appointments = result.json()
    total = 0
    for appt in appointments:
        total += decimal.Decimal(appt.get('price'))
        appt['start_time_formatted'] = parse(appt.get('start_time'))

    today = datetime.now().strftime('%Y-%m-%d')
    rand = random.choice(range(100,999))
    invoice_number = '{}-{}'.format(today.replace('-',''), rand)

    context = {
        "appointments": appointments,
        "total": total,
        "invoice_number": invoice_number,
    }

    return render(request, 'invoice/templates/basic.html', context=context)


# docker run -v $(pwd):/downloads/ aquavitae/weasyprint weasyprint http://weasyprint.org /downloads/invoice.pdf

import docker, os
client = docker.from_env()
volumes = { os.getcwd(): { 'bind': '/downloads/' } }
client.containers.run("aquavitae/weasyprint", "weasyprint http://weasyprint.org /downloads/invoice.pdf", volumes=volumes)

client.containers.run('alpine', 'echo hello world')
"""
