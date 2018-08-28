from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone
import uuid, requests, os

from .guru import publish
from .mixins import InvoiceModelMixin

from decimal import Decimal
from dateutil.parser import parse
from datetime import datetime, timedelta

INVOICE_STATUSES = [
    ('new', 'new'),
    ('sent', 'sent'),
    ('paid', 'paid'),
    ('unpaid', 'unpaid'),
]

PAYMENT_METHODS = [
    ('eft', 'eft'),
    ('cash', 'cash'),
    ('snapscan', 'snapscan'),
    ('credit_card', 'credit_card'),
    ('write_off', 'write_off'),
    ('unknown', 'unknown'),
    ('medicalaid', 'medicalaid'),
    ('gift', 'gift'),
    ('voucher', 'voucher'),
]

# fields that will get mapped from
# context to fields on an invoice
EXTRA_FIELDS = [
    'practitioner_id',
    'customer_id',
    'title',
    'invoice_period_from',
    'invoice_period_to',
    'sender_email',
    'date',
    'due_date',
    'status'
]

TEMPLATES = [(key, '{} - {}'.format(key, values.get('title'))) for key, values in settings.TEMPLATE_REGISTRY.items()]

def get_uuid():
  return str(uuid.uuid4())

def get_short_uuid():
    return str(uuid.uuid4()).split('-')[0]

"""
class InvoiceSettings(models.Model):

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name =  models.CharField(max_length=255, blank=True, null=True)

    # configs:
    template = models.CharField(max_length=255, blank=True, null=True, help_text='The base template to use for invoices using these settings')
"""


class InvoiceSettings(models.Model):
    '''
    Global settings that apply to all generated invoices
    '''

    collection = 'invoices_settings'
    serializer_path = 'invoice.serializers.InvoiceSettingsSerializer'
    readonly_sync = True

    def __str__(self):
        return 'Settings for Practitioner #{}'.format(self.practitioner_id)

    practitioner_id = models.CharField(max_length=128, db_index=True)
    quote_notes = models.TextField(blank=True, null=True)
    invoice_notes = models.TextField(blank=True, null=True)
    receipt_notes = models.TextField(blank=True, null=True)

    billing_address = models.TextField(blank=True, null=True, help_text='The address of the billing party')

    customer_info = models.TextField(blank=True, null=True, verbose_name='Customer info template', help_text='Choose how you would like to display your customers info')
    lineitem_template = models.TextField(blank=True, null=True, default='codetable.html')

    include_booking_info = models.NullBooleanField(default=True)
    integrate_medical_aid = models.NullBooleanField(default=False)
    show_snapcode_on_invoice = models.NullBooleanField(default=False)
    allow_pre_payments = models.NullBooleanField(default=False)
    allow_submit_to_medical_aid = models.NullBooleanField(default=False)
    snap_id = models.CharField(max_length=128, blank=True, null=True)

    include_vat = models.NullBooleanField(default=False)
    vat_percent = models.PositiveIntegerField(default=0, blank=True, null=True)

class Invoice(models.Model, InvoiceModelMixin):

    collection = 'invoices'
    serializer_path = 'invoice.serializers.InvoiceSerializer'
    readonly_sync = True

    def __str__(self):
        return '#{}: {}'.format(self.invoice_number, self.title)

    # relationships
    practitioner_id = models.CharField(max_length=128, db_index=True)
    customer_id = models.CharField(max_length=128, db_index=True)
    appointments = ArrayField(models.CharField(max_length=100, blank=True, null=True), default=[], db_index=True, blank=True, null=True)

    object_ids = ArrayField(models.CharField(max_length=100), default=[], db_index=True)

    sender_email = models.EmailField(default='support@appointmentguru.co')
    # invoice_number = models.CharField(max_length=255,blank=True, null=True)
    title = models.CharField(max_length=255,blank=True, null=True)
    status = models.CharField(max_length=10, choices=INVOICE_STATUSES, default='new', db_index=True)

    context = JSONField(default={})
    template = models.CharField(max_length=255, blank=True, null=True, choices=TEMPLATES, default='basic_v2')

    password = models.CharField(max_length=255, blank=True, null=True, default=get_short_uuid)
    customer_password = models.CharField(max_length=255, blank=True, null=True, default=get_short_uuid)

    currency = models.CharField(max_length=4,blank=True, null=True, default='ZAR')
    invoice_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)

    date = models.DateField(default=timezone.localdate, db_index=True, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True, db_index=True)

    invoice_period_from = models.DateField(db_index=True, blank=True, null=True)
    invoice_period_to = models.DateField(db_index=True, blank=True, null=True)

    short_url = models.URLField(blank=True, null=True)

    integrate_medical_aid = models.NullBooleanField()
    # free text fields:
    billing_address = models.TextField(blank=True, null=True)
    invoicee_details = models.TextField(blank=True, null=True)
    medicalaid_details = models.TextField(blank=True, null=True)


    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

    @staticmethod
    def past_due(min_days, max_days = None, other_filters = None):

        if other_filters is None: other_filters = {}
        now = timezone.now()
        to_date = now - timedelta(days=min_days)

        filters = {
            "due_date__lte": to_date
        }

        if max_days is not None:
            from_date = now - timedelta(days=max_days)
            filters.update({
                "due_date__gte": from_date
            })

        filters.update(other_filters)
        invoices =  Invoice.objects.filter(**filters).order_by('-due_date')
        invoices = invoices.exclude(status='paid')
        return invoices

    @classmethod
    def from_appointment(cls, practitioner_id, appointment_id, with_save=True, send=False):
        instance = cls()
        builder = InvoiceBuilder(instance)
        appointments = builder.get_appointments(practitioner_id, [appointment_id])

        if len(appointments) > 0:
            appointment = appointments[0]
            dt = parse(appointment.get('end_time')).date()
            client_id = appointment.get('client_id') or appointment.get('client', {}).get('id')

            instance.customer_id = client_id
            instance.practitioner_id = practitioner_id
            instance.appointments = [appointment_id]
            instance.date = dt
            instance.due_date = dt
            instance.invoice_period_from = dt
            instance.invoice_period_to = dt
            instance.template = 'basic_v2'
            if appointment.get('status') == 'P':
                instance.status = 'paid'

            if with_save:
                instance.save()

            if send:
                instance.send(to_email=True)
            return instance
        return None



TRANSACTION_TYPES = [
    ('Invoice', 'Invoice'),
    ('Payment', 'Payment'),
]

class Transaction(models.Model):

    collection = 'transactions'
    serializer_path = 'invoice.serializers.TransactionSerializer'
    readonly_sync = True

    def __str__(self):
        arrow = '->'
        if self.type == 'Payment':
            arrow = '<-'
        return "#{}: {} {} {}. {}".format(
            self.invoice.id,
            self.practitioner_id,
            arrow,
            self.customer_id,
            self.amount
        )

    practitioner_id = models.CharField(max_length=128, db_index=True)
    customer_id = models.CharField(max_length=128, db_index=True)
    actor_id = models.CharField(max_length=128, db_index=True)

    invoice = models.ForeignKey(Invoice, blank=True, null=True)

    auto_created = models.BooleanField(default=False, db_index=True, help_text='Checked if this transactions was automatically created by the system')
    appointments = ArrayField(models.CharField(max_length=100, blank=True, null=True), default=[], db_index=True, blank=True, null=True)

    type = models.CharField(max_length=10,blank=True, null=True, choices=TRANSACTION_TYPES, db_index=True)

    currency = models.CharField(max_length=4,blank=True, null=True, default='ZAR')
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)
    method = models.CharField(max_length=128, choices=PAYMENT_METHODS, db_index=True)
    date = models.DateTimeField(db_index=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

    @classmethod
    def from_invoice(cls, invoice, transaction_type='Invoice', method='unknown', date=None, amount=None, auto_created=True, with_save=True):
        '''
        Creates a transaction from an invoice.
        If invoice is not in correct status, returns None

        raises TransactionAlreadyExists error if a matching transaction already exists

        '''

        # There can only be 1 invoice-type transaction / invoice
        if transaction_type == 'Invoice':
            existing_transactions = Transaction.objects.filter(
                invoice=invoice,
                type='Invoice'
            )
            if existing_transactions.count() > 0:
                transaction = existing_transactions.first()
                if transaction.amount != invoice.invoice_amount:
                    transaction.amount = invoice.invoice_amount
                    transaction.save()
                return transaction

        transaction = cls()
        copy_fields = ['practitioner_id', 'customer_id', 'appointments']
        for field in copy_fields:
            value = getattr(invoice, field)
            setattr(transaction, field, value)

        if date is None:
            date = invoice.modified_date

        transaction.type = transaction_type

        transaction.auto_created = auto_created
        transaction.invoice_id = invoice.id
        if amount is None:
            transaction.amount = invoice.amount_due
        else:
            transaction.amount = Decimal(amount)
        transaction.date = date
        # transaction.transaction_date = invoice.created_date
        transaction.method = method
        if with_save:
            transaction.save()
        return transaction


def proof_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    filename_base, filename_ext = os.path.splitext(filename)
    # return 'practitioner/images/{}/profile{}'.format(instance.user_id, filename_ext)
    invoice = instance.invoice
    return 'proofs/{}/{}/filename_base{}'.format(invoice.practitioner_id, invoice.id, filename_ext)

class ProofOfPayment(models.Model):

    invoice = models.ForeignKey(Invoice)
    transaction = models.ForeignKey(Transaction, blank=True, null=True)
    document = models.FileField(upload_to=proof_upload_path, blank=True, null=True) # <- ideally this should really be required. Just for testing :()
    approved = models.BooleanField(default = False)

    medical_aid_email = models.EmailField(null=True, blank=True)
    auto_submit_to_medical_aid = models.BooleanField(default=False)

    def approve(self):
        self.approved = True
        self.save()
        self.invoice.status = 'sent'
        payment = Transaction.from_invoice(self.invoice)
        payment.proofofpayment_set.add(self)
        payment.save()
        if self.auto_submit_to_medical_aid:
            print('Send to medical aid: {}'.format(self.medical_aid_email))


# class Action(models.Model):
#     invoice = models.ForeignKey(Invoice, blank=True, null=True)
#     payment = models.ForeignKey(Payment, blank=True, null=True)
#     actor = models.CharField()

from .signals import *
# from django_nosql.signals import (
#     sync_readonly_db,
#     sync_remove_readonly_db
# )
