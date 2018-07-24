'''
Views for displaying invoices
'''
from django.urls import reverse
from dateutil.parser import parse
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from decimal import Decimal
from dateutil import parser
from datetime import datetime, timedelta, date
import json, calendar

from .helpers import (
    fetch_data,
    to_context,
    codes_to_table,
    combine_into_transactions
)

from .models import Invoice, InvoiceSettings, Payment, ProofOfPayment
from .medialaids import MEDIAL_AIDS
from .forms import (
    UpdateInvoiceDetailsForm,
    ProofOfPaymentForm,
    MedicalAidSubmissionForm,
    QuickInvoiceForm,
)
from .tasks import mark_invoice_as_paid

def __get_invoice(request, pk):
    password = request.GET.get('key')
    invoice = get_object_or_404(Invoice, pk=pk, password=password)
    try:
        invoice_settings = InvoiceSettings.objects.get(practitioner_id = invoice.practitioner_id)
    except InvoiceSettings.DoesNotExist:
        invoice_settings = None

    return (invoice, invoice_settings)

@csrf_exempt
def snap_webhook(request):
    print(request.POST.get('payload'))
    data = json.loads(request.POST.get('payload'))
    invoice_id = data.get('extra').get('invoiceId')

    try:
        data = {
            "invoice_id": invoice_id,
            "payment_method": "snapscan",
            "options": { "send_receipt": True }
        }
        mark_invoice_as_paid(data)
    except Invoice.DoesNotExist:
        data.update({
            "error": "No matching invoice found"
        })

    # keen.add_event("snapscan_webhook", data)
    return HttpResponse('ok')

@user_passes_test(lambda u: u.is_superuser)
def test_invoices(request):
    form = QuickInvoiceForm()
    if request.method == 'POST':
        form = QuickInvoiceForm(request.POST)
        if form.is_valid():
            invoice = form.save()
            return HttpResponseRedirect(invoice.get_view_url)

    context = {
        "invoices": Invoice.objects.filter(practitioner_id=1, template='basic_v2').order_by('-id'),
        "form": form
    }
    return render(request, 'invoice/test.html', context=context)

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
    '''
from invoice.models import *
practitioner=7
payments = Payment.objects.filter(practitioner_id=practitioner).order_by('payment_date')[0:10]

possible time periods:

- days=14
- from_date + to_date
- month + year
    '''

    month = int(request.GET.get('month', date.today().month))
    year = int(request.GET.get('year', date.today().year))
    last_day = calendar.monthrange(year, month)[1]

    start_date = date(year, month, 1)
    end_date = date(year, month, last_day)

    invoices = Invoice.objects.filter(
        practitioner_id=practitioner,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')
    payments = Payment.objects.filter(
        practitioner_id=practitioner,
        payment_date__gte=start_date,
        payment_date__lte=end_date
    ).order_by('payment_date')

    transactions = combine_into_transactions(invoices, payments)
    print(transactions)
    context = {
        "transactions": transactions
    }
    return render(request, 'invoice/transactions.html', context=context)

def statement(request, practitioner, client):
    from_date = date(2018,1,1)
    invoices = Invoice.objects.filter(
        practitioner_id=practitioner,
        customer_id=client,
        date__gte=from_date
    ).order_by('-date')
    payments = Payment.objects.filter(
        practitioner_id=practitioner,
        customer_id=client,
        payment_date__gte=from_date
    ).order_by('-payment_date')

    settings = InvoiceSettings.objects.get(practitioner_id = practitioner)
    transactions = combine_into_transactions(invoices, payments)

    balance_brought_forward = 0
    amount_paid = payments.aggregate(amount_paid=Sum('amount')).get('amount_paid')
    amount_due = invoices.aggregate(amount_due=Sum('invoice_amount')).get('amount_due')

    statement_date = parser.parse('2018-01-01')
    statement_due_date = parser.parse('2018-07-30')

    invoice = invoices.first()
    client = invoice.context.get("client")
    practitioner = invoice.context.get("practitioner")

    # amount_paid = 0
    # amount_due = invoices.aggregate(amount_due=Sum('invoice_amount')).get('amount_due')

    balance = {
        "outstanding": balance_brought_forward,
        "paid": amount_paid,
        "due": amount_due,
        "diff": (amount_due - amount_paid)
    }
    context = {
        "transactions": transactions,
        "settings": settings,
        "invoices": invoices,
        "invoice": invoice,
        "client": client,
        "practitioner": practitioner,
        "payments": payments,
        "balance": balance,
        "statement_date": statement_date,
        "statement_due_date": statement_due_date
    }

    return render(request, 'invoice/statement.html', context=context)

def edit_invoice(request, pk):
    password = request.GET.get('key')
    invoice = get_object_or_404(Invoice, pk=pk, password=password)
    try:
        invoice_settings = InvoiceSettings.objects.get(practitioner_id = invoice.practitioner_id)
    except InvoiceSettings.DoesNotExist:
        invoice_settings = None

    if request.method == 'POST':
        form = UpdateInvoiceDetailsForm(request.POST)
        if form.is_valid():
            form.save(invoice)
            url = reverse('view_invoice_view', args=(invoice.id,))
            url = "{}?key={}".format(url, invoice.password)
            return HttpResponseRedirect(url)
    else:
        form = UpdateInvoiceDetailsForm.from_customer(invoice.customer_id, invoice.practitioner_id)

    ignored_fields = ['medicalaid', 'name']
    context = {
        "page_title": "Your details",
        "invoice": invoice,
        "form": form,
        "medicalaids": form.get_medicalaids(),
        "ignored_fields": ignored_fields,
    }
    return render(request, 'invoice/edit.html', context=context)

def submit_invoice(request, pk):

    invoice, settings = __get_invoice(request, pk)
    message = None
    medical_aid, medical_aids = MedicalAidSubmissionForm.get_medicalaid(invoice)
    if request.method == 'POST':
        form = MedicalAidSubmissionForm(request.POST)
        if form.is_valid():
            form.save(invoice)
            claimed_email = form.cleaned_data.get('claims_email')
            message = "Receipt has been submitted to {}".format(claimed_email)
    else:
        initial = {
            "customer_email": invoice.get_client_email
        }
        if medical_aid is not None:
            initial['claims_email'] = medical_aid.get('email')
        form = MedicalAidSubmissionForm(initial=initial)

    context = {
        "invoice": invoice,
        "settings": settings,
        "medical_aid": medical_aid,
        "medical_aids": medical_aids,
        "form": form,
        "message": message,
    }
    return render(request, 'invoice/submit.html', context=context)

def pay_invoice(request, pk):

    password = request.GET.get('key')
    invoice = get_object_or_404(Invoice, pk=pk, password=password)
    try:
        invoice_settings = InvoiceSettings.objects.get(practitioner_id = invoice.practitioner_id)
    except InvoiceSettings.DoesNotExist:
        invoice_settings = None

    pop = ProofOfPayment()
    pop.invoice = invoice
    if request.method == 'POST':
        form = ProofOfPaymentForm(request.POST, request.FILES, instance=pop)
        if form.is_valid():
            form.save()
    else:
        form = ProofOfPaymentForm(instance=pop)

    if invoice.status == 'paid':
        amount_paid = invoice.invoice_amount
    else:
        amount_paid = Decimal(invoice.amount_paid)

    amount_due = Decimal(invoice.invoice_amount) - amount_paid

    snap_params = "?invoice_id={}&amount={}".format(invoice.id, format(amount_due, '.2f').replace('.', ''))
    context = {
        "invoice": invoice,
        "settings": invoice_settings,
        "snap_params": snap_params,
        "amount_due": amount_due,
        "form": form
    }

    return render(request, 'invoice/pay.html', context=context)

def view_invoice(request, pk):

    invoice, invoice_settings = __get_invoice(request, pk)
    message = None
    if request.GET.get('send') is not None:
        invoice.send(to_email=True)
        message = "Invoice sent to : {}".format(invoice.get_client_email)

    context = {
        "page_title": "Invoice #: {}".format(invoice.invoice_number),
        "message": message,
        "invoice": invoice,
        "settings": invoice_settings,
        "invoiceguru_url": settings.INVOICEGURU_BASE_URL,
    }
    return render(request, 'invoice/view.html', context=context)
    # return render(request, 'invoice/app.html', context=context)

@csrf_exempt
def invoice(request, pk):
    password = request.GET.get('key')
    invoice = get_object_or_404(Invoice, pk=pk, password=password)

    template_key = request.GET.get('template', invoice.template)
    template_data = settings.TEMPLATE_REGISTRY.get(template_key)
    template_path = 'invoice/templates/{}'.format(template_data.get('filename', 'basic.html'))
    template_path = 'invoice/templates/basic_v2.html'
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
