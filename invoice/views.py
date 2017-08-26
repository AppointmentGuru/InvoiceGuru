import json
from dateutil.parser import parse
from django.conf import settings
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def invoice(request):

    context = {}

    try:
        context.update(json.loads(request.body))
    except json.decoder.JSONDecodeError:
        pass

    template_key = request.GET.get('template', 'basic')
    template_data = settings.TEMPLATE_REGISTRY.get(template_key)
    template_path = 'invoice/templates/{}'.format(template_data.get('filename', 'basic.html'))

    for appt in context.get('appointments', []):
        appt['start_time_formatted'] = parse(appt.get('start_time'))

    return render(request, template_path, context=context)

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
