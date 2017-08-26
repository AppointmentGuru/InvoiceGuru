import json
from dateutil.parser import parse
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from .models import Invoice

@csrf_exempt
def invoice(request, pk):

    invoice = get_object_or_404(Invoice, pk=pk)

    template_key = request.GET.get('template', 'basic')
    template_data = settings.TEMPLATE_REGISTRY.get(template_key)
    template_path = 'invoice/templates/{}'.format(template_data.get('filename', 'basic.html'))

    context = invoice.context
    for appt in context.get('appointments', []):
        appt['start_time_formatted'] = parse(appt.get('start_time'))

    return render(request, template_path, context=context)


# docker run -v $(pwd):/downloads/ aquavitae/weasyprint weasyprint http://weasyprint.org /downloads/invoice.pdf

# import docker, os
# client = docker.from_env()
# volumes = { os.getcwd(): { 'bind': '/downloads/' } }
# client.containers.run("aquavitae/weasyprint", "weasyprint http://weasyprint.org /downloads/invoice.pdf", volumes=volumes)

# client.containers.run('alpine', 'echo hello world')
