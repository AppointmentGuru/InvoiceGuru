import json
from dateutil.parser import parse
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .helpers import fetch_data, to_context
from .models import Invoice

@csrf_exempt
def invoice(request, pk):
    password = request.GET.get('key')
    invoice = get_object_or_404(Invoice, pk=pk, password=password)

    template_key = request.GET.get('template', invoice.template)
    template_data = settings.TEMPLATE_REGISTRY.get(template_key)
    template_path = 'invoice/templates/{}'.format(template_data.get('filename', 'basic.html'))

    context = invoice.context
    for appt in context.get('appointments', []):
        appt['start_time_formatted'] = parse(appt.get('start_time'))

    return render(request, template_path, context=context)

@csrf_exempt
def preview(request):
    practitioner_id = request.GET.get('practitioner_id')
    appointment_ids = request.GET.get('appointment_ids', '').split(',')
    client_id = request.GET.get('client_id')

    practitioner, appointments, medical_record = fetch_data(practitioner_id, appointment_ids, client_id)
    context = to_context(practitioner, appointments, medical_record)
    return render(request, 'invoice/templates/basic.html', context=context)

# docker run -v $(pwd):/downloads/ aquavitae/weasyprint weasyprint http://weasyprint.org /downloads/invoice.pdf

# import docker, os
# client = docker.from_env()
# volumes = { os.getcwd(): { 'bind': '/downloads/' } }
# client.containers.run("aquavitae/weasyprint", "weasyprint http://weasyprint.org /downloads/invoice.pdf", volumes=volumes)

# client.containers.run('alpine', 'echo hello world')
