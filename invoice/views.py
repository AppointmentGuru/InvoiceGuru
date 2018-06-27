'''
Views for displaying invoices
'''
from dateutil.parser import parse
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from decimal import Decimal
from dateutil import parser
from datetime import datetime
import json

from .helpers import (
    fetch_data,
    to_context,
    codes_to_table,
    get_invoice_template
)
from .models import Invoice, InvoiceSettings, Payment
from .medialaids import MEDIAL_AIDS
from .forms import UpdateInvoiceDetailsForm

@csrf_exempt
def snap_webhook(request):
    print(request.POST.get('payload'))
    data = json.loads(request.POST.get('payload'))
    invoice_id = data.get('extra').get('invoiceId')

    try:
        invoice = Invoice.objects.get(id=invoice_id)
        invoice.status = 'paid'
        invoice.save()
        invoice.publish()
    except Invoice.DoesNotExist:
        data.update({
            "error": "No matching invoice found"
        })

    # keen.add_event("snapscan_webhook", data)
    return HttpResponse('ok')

@user_passes_test(lambda u: u.is_superuser)
def test_invoices(request):
    context = {
        "invoices": Invoice.objects.all().order_by('?')[0:10]
    }
    return render(request, 'invoice/listall.html', context=context)

@user_passes_test(lambda u: u.is_superuser)
def invoices(request, practitioner, from_date, to_date):
    '''
    '''
    parsed_from = parser.parse(from_date)
    parsed_to = parser.parse(to_date)
    invoices = Invoice.objects.filter(
        practitioner_id=practitioner,
        date__gte=parsed_from,
        date__lte=parsed_to)

    total_value = sum([invoice.invoice_amount for invoice in invoices])
    context = {
        'invoices': invoices,
        'parsed_from': parsed_from,
        'parsed_to': parsed_to,
        'total_value': total_value,
    }
    return render(request, 'invoice/list.html', context=context)

def transactions(request, practitioner):

    invoices = Invoice.objects.filter(practitioner_id=practitioner)
    payments = Payment.objects.filter(practitioner_id=practitioner)

    return render(request, 'invoice/transactions.html', context=context)

def statement(request, practitioner, client):

    invoices = Invoice.objects.filter(practitioner_id=practitioner, customer_id=client)
    payments = Payment.objects.filter(practitioner_id=practitioner, customer_id=client)

    amount_paid = payments.aggregate(amount_paid=Sum('amount')).get('amount_paid')
    amount_due = invoices.aggregate(amount_due=Sum('invoice_amount')).get('amount_due')

    statement_date = parser.parse('2018-04-25')
    statement_due_date = parser.parse('2018-04-30')
    invoices = Invoice.objects.filter(id=1692)

    amount_paid = 0
    amount_due = invoices.aggregate(amount_due=Sum('invoice_amount')).get('amount_due')

    balance = {
        "paid": amount_paid,
        "due": amount_due,
        "diff": (amount_due - amount_paid)
    }
    context = {
        "invoices": invoices,
        "payments": payments,
        "balance": balance,
        "statement_date": statement_date,
        "statement_due_date": statement_due_date
    }

    return render(request, 'invoice/statement.html', context=context)

def diy_invoice(request, pk):
    password = request.GET.get('key')
    invoice = get_object_or_404(Invoice, pk=pk, password=password)
    template = get_invoice_template(invoice)

    if request.method == 'POST':
        form = UpdateInvoiceDetailsForm(request.POST)
        print(request.POST)
        if form.is_valid():
            form.save(invoice)
            template = 'invoice/view.html'
    else:
        form = UpdateInvoiceDetailsForm()

    try:
        first_appointment = invoice.context.get('appointments')[0]
    except IndexError:
        first_appointment = {}

    medical_aid_details = invoice.context.get('medicalaid_info')
    if medical_aid_details is not None:
        medical_aid_details = medical_aid_details.split('\n')

    client_details = first_appointment.get("client", {})

    medial_aids_quickpick = [
        {"name": 'DISCOVERY Health Medical Scheme', "email": 'claims@discovery.co.za'},
        {"name": 'BONITAS Medical Fund', "email": 'claims@bonitas.co.za'},
        {"name": 'COMPCare WELLNESS Medical Scheme', "email": 'claims@universal.co.za'},
        {"name": 'PROFMED', "email": 'claims@profmed.co.za'}
    ]
    ignored_fields = ['medical_aid']
    context = {
        "page_title": "Invoice #:",
        "invoice": invoice,
        "form": form,
        "ignored_fields": ignored_fields,
        "client": client_details,
        "medical_aid": medical_aid_details,
        "medial_aids_quickpick": medial_aids_quickpick,
        "medical_aids": MEDIAL_AIDS
    }
    return render(request, template, context=context)
    # return render(request, 'invoice/app.html', context=context)

@csrf_exempt
def invoice(request, pk):
    password = request.GET.get('key')
    invoice = get_object_or_404(Invoice, pk=pk, password=password)

    template_key = request.GET.get('template', invoice.template)
    template_data = settings.TEMPLATE_REGISTRY.get(template_key)
    template_path = 'invoice/templates/{}'.format(template_data.get('filename', 'basic.html'))
    # template_path = 'invoice/templates/material.html'

    context = invoice.context
    invoice_total = 0
    amount_paid = 0
    for appt in context.get('appointments', []):
        appt['start_time_formatted'] = parse(appt.get('start_time'))
        codes = appt.get('codes', None)
        if codes is not None and len(codes) > 0:
            appt['codes_formatted'] = codes_to_table(codes)
        if appt.get('status') == 'P':
            amount_paid += Decimal(appt.get('price', 0))
        invoice_total += Decimal(appt.get('price', 0))

    try:
        invoice_settings = InvoiceSettings.objects.get(practitioner_id = invoice.practitioner_id)
    except InvoiceSettings.DoesNotExist:
        invoice_settings = None

    is_receipt = False
    if invoice.status == 'paid':
        amount_paid = invoice.invoice_amount
    else:
        amount_paid = Decimal(invoice.amount_paid)

    amount_due = Decimal(invoice.invoice_amount) - amount_paid

    if amount_due == 0:
        is_receipt = True

    context['invoice'] = invoice
    context['is_receipt'] = is_receipt
    context['amount_paid'] = amount_paid
    context['amount_due'] = amount_due
    context['settings'] = invoice_settings
    context['snap_params'] = "?invoice_id={}&amount={}".format(
        invoice.id,
        format(amount_due, '.2f').replace('.', ''))

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
