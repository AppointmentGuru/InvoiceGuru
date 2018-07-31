from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
from django.utils import timezone
import uuid, requests, os

from .guru import publish

from .helpers import (
    fetch_data,
    to_context,
    clean_context
)
from dateutil.parser import parse
from datetime import datetime

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
    include_vat = models.NullBooleanField(default=False)

    snap_id = models.CharField(max_length=128, blank=True, null=True)
    vat_percent = models.PositiveIntegerField(default=0, blank=True, null=True)

class Invoice(models.Model):

    cached_settings = None

    def __str__(self):
        return '#{}: {}'.format(self.invoice_number, self.title)

    def get_absolute_url(self):
        return '/invoice/view/{}/?key={}'.format(self.id, self.password)

    @property
    def amount_due(self):
        due = self.invoice_amount - self.amount_paid
        return format(due, '.2f')

    @property
    def get_download_url(self):
        return '/invoice/{}/?key={}'.format(self.id, self.password)

    @property
    def get_view_url(self):
        return '/invoice/view/{}/?key={}'.format(self.id, self.password)

    def __get_snap_url(self, is_qr_code=True):
        base = "https://pos.snapscan.io/qr/"
        snap_id = self.settings.snap_id
        if is_qr_code:
            snap_id = "{}.svg".format(snap_id)
        snap_params = "?invoice_id={}&amount={}".format(
            self.id,
            self.amount_due.replace('.', '')
        )
        return "{}{}{}&strict=true".format(
            base,
            snap_id,
            snap_params
        )

    @property
    def show_snapcode_on_invoice(self):
        return self.settings.show_snapcode_on_invoice

    @property
    def get_snapscan_url(self):
        return self.__get_snap_url(is_qr_code=False)

    @property
    def get_snapscan_qr(self):
        return self.__get_snap_url(is_qr_code=True)

    @property
    def settings(self):
        if self.cached_settings is not None:
            return self.cached_settings
        try:
            settings = InvoiceSettings.objects.get(practitioner_id = self.practitioner_id)
            self.cached_settings = settings
            return settings
        except InvoiceSettings.DoesNotExist:
            return None


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
    template = models.CharField(max_length=255, blank=True, null=True, choices=TEMPLATES, default='basic')

    password = models.CharField(max_length=255, blank=True, null=True, default=get_short_uuid)
    customer_password = models.CharField(max_length=255, blank=True, null=True, default=get_short_uuid)

    currency = models.CharField(max_length=4,blank=True, null=True, default='ZAR')
    invoice_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)

    date = models.DateField(default=timezone.now, db_index=True, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True, db_index=True)

    invoice_period_from = models.DateField(db_index=True, blank=True, null=True)
    invoice_period_to = models.DateField(db_index=True, blank=True, null=True)

    short_url = models.URLField(blank=True, null=True)

    # free text fields:
    invoicee_details = models.TextField(blank=True, null=True)
    medicalaid_details = models.TextField(blank=True, null=True)

    # settings:
    integrate_medical_aid = models.NullBooleanField()
    # automatically_submit_to_medical_aid = models.BooleanField(default=False)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

    def __get_client(self):
        client = self.context.get("client")
        if client is not None:
            return client

        appointments = self.context.get("appointments", [])
        if len(appointments) > 0:
            client = appointments[0].get("client")
            IS_CLIENT_ID = isinstance(client, int)
            if IS_CLIENT_ID:
                name = appointment.get("full_name")
                return {
                    "first_name": name.split(" ")[0],
                    "last_name": (" ").join(name.split(" ")[1:]),
                    "email": appointment.get("contact_email"),
                    "phone_number": appointment.get("contact_phone"),
                }
            return client
        return {}

    @classmethod
    def from_appointment(cls, practitioner_id, appointment_id, with_save=True, send=False):
        instance = cls()
        builder = InvoiceBuilder(instance)
        appointments = builder.get_appointments(practitioner_id, [appointment_id])

        if len(appointments) > 0:
            appointment = appointments[0]
            dt = parse(appointment.get('start_time')).date()
            title = appointment.get('invoice_title') or appointment.get('title')
            client_id = appointment.get('client_id') or appointment.get('client', {}).get('id')

            instance.customer_id = client_id
            instance.practitioner_id = practitioner_id
            instance.appointments = [appointment_id]
            instance.date = dt
            instance.due_date = dt
            instance.title = title
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

    @property
    def get_client_email(self):
        return self.__get_client().get("email")

    @property
    def get_client_full_name(self):
        fname = self.__get_client().get("first_name")
        lname = self.__get_client().get("last_name")
        return "{} {}".format(fname, lname)

    @property
    def get_client_phone_number(self):
        return self.__get_client().get("phone_number")

    def get_short_url(self, force=False, admin_url=True):
        '''
        curl https://www.googleapis.com/urlshortener/v1/url?key=... \
            -H 'Content-Type: application/json' \
            -d '{"longUrl": "https://google.com"}'
        '''
        url = 'https://www.googleapis.com/urlshortener/v1/url'
        params = {
            "key": settings.GOOGLE_API_SHORTENER_TOKEN
        }

        if admin_url:
            url_to_shorten = self.admin_invoice_url
        else:
            url_to_shorten = self.customer_invoice_url

        result = requests.post(
            url,
            json={'longUrl': url_to_shorten},
            params=params)
        short_url = result.json().get('id')
        self.short_url = short_url
        self.save()
        return short_url

    def enrich(self):
        return InvoiceBuilder(self).enrich()

    def get_context(self, default_context = {}):

        practitioner, appointments, medical_record = fetch_data(
            self.practitioner_id,
            self.appointment_ids,
            self.customer_id)

        context = to_context(
                    practitioner,
                    appointments,
                    medical_record,
                    default_context=default_context,
                    format_times = False,
                    format_codes = False)
        context = clean_context(context)
        self.context = context
        return context

    def apply_settings(self, with_save=True):
        if self.settings is not None:
            fields = dir(InvoiceSettings)
            for field in fields:
                IS_PRIVATE_FIELD = field.startswith('_')
                EXISTS = hasattr(self, field)

                if not IS_PRIVATE_FIELD and EXISTS:
                    FIELD_IS_EMPTY = getattr(self, field, None) is None
                    if FIELD_IS_EMPTY:
                        value = getattr(self.settings, field)
                        setattr(self, field, value)
            if with_save:
                self.save()

    def apply_context(self):
        '''
        Copy items from context to invoice
        '''
        for field in EXTRA_FIELDS:
            value = self.context.get(field, None)
            if value is not None:
                setattr(self, field, value)


    def _get_serialized(self):
        from .serializers import InvoiceSerializer
        if isinstance(self.date, datetime):
            self.date = self.date.date() # make sure date is only a date
        return InvoiceSerializer(self).data

    def _get_payload(self):
        data = self._get_serialized()
        summarized = [{"id": appt.get('id')} \
                    for appt \
                    in data.get('context',{}).get('appointments')]
        data.update({"context": { "appointments": summarized } })
        return data

    def send(self, to_email=False, to_phone=False, to_inapp = False):

        from .tasks import send_invoice_or_receipt
        data = {
            "from_email": self.sender_email,
            "invoice_id": self.id
        }
        if to_email and self.get_client_email:
            data.update({
                "to_emails": [self.get_client_email]
            })
        if to_phone and self.get_client_phone_number:
            data.update({
                "to_phone_numbers": [self.get_client_phone_number]
            })
        if to_inapp and self.get_client_phone_number:
            data.update({
                "to_channels": [self.get_client_phone_number]
            })
        return send_invoice_or_receipt(data)

    def send_to_medical_aid(self):
        pass

    def publish(self):
        if self.status == 'paid':
            self.publish_paid()
        if self.status == 'sent':
            self.publish_sent()

    def publish_paid(self):
        data = self._get_payload()
        publish(settings.PUBLISHKEYS.invoice_paid, data)

    def publish_sent(self):
        data = self._get_payload()
        publish(settings.PUBLISHKEYS.invoice_sent, data)

    @property
    def is_receipt(self):
        return self.status == 'paid'
        # return (self.invoice_amount - self.amount_paid) == 0

    @property
    def invoice_number(self):
        if self.title is None: return 'INV-{}'.format(self.id)
        initials = ("").join([word[0:1].upper() for word in self.title.split(' ') if word.isalpha()])
        return '{}-{}'.format(initials, self.id)

    @property
    def admin_invoice_url(self):
        base = settings.INVOICEGURU_BASE_URL
        return '{}/invoice/{}?key={}'.format(base, self.pk, self.password)

    @property
    def customer_invoice_url(self):
        base = settings.INVOICEGURU_BASE_URL
        return '{}/invoice/{}?key={}'.format(base, self.pk, self.customer_password)

TRANSACTION_TYPES = [
    ('Invoice', 'Invoice'),
    ('Payment', 'Payment'),
]

class Transaction(models.Model):

    def __str__(self):
        return "{} -> {}. {}".format(
            self.customer_id,
            self.practitioner_id,
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
    def from_invoice(cls, invoice, method='unknown', date=None, with_save=True):
        '''
        Creates a transaction from an invoice. 
        If invoice is not in correct status, returns None 

        raises TransactionAlreadyExists error if a matching transaction already exists

        '''

        if invoice.status not in ['paid', 'sent']:
            return None
        
        transaction_type = 'Invoice'
        if invoice.status == 'paid':
            transaction_type = 'Payment'

        # check for dupes:
        existing_transactions = Transaction.objects.filter(
            invoice=invoice, 
            auto_created=True,
            type=transaction_type
        )
        if existing_transactions.count() > 0:
            print("transaction already exists")
            return existing_transactions.first()

        transaction = cls()
        copy_fields = ['practitioner_id', 'customer_id', 'appointments']
        for field in copy_fields:
            value = getattr(invoice, field)
            setattr(transaction, field, value)

        if date is None:
            date = invoice.modified_date

        transaction.type = transaction_type
        
        transaction.auto_created = True 
        transaction.invoice_id = invoice.id
        transaction.amount = invoice.amount_paid
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