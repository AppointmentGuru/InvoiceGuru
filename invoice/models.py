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

    invoice_address = models.TextField(blank=True, null=True, help_text='Your address as shown on invoices' )
    customer_info = models.TextField(blank=True, null=True, help_text='Choose how you would like to display your customers info')
    lineitem_template = models.TextField(blank=True, null=True, default='codetable.html')

    include_booking_info = models.BooleanField(default=True)

    integrate_medical_aid = models.BooleanField(default=False)

    snap_id = models.CharField(max_length=128, blank=True, null=True)
    show_snapcode_on_invoice = models.BooleanField(default=False)
    allow_pre_payments = models.BooleanField(default=False)
    allow_submit_to_medical_aid = models.BooleanField(default=False)

    include_vat = models.BooleanField(default=False)
    vat_percent = models.PositiveIntegerField(default=0, blank=True, null=True)


class Invoice(models.Model):

    def __str__(self):
        return '#{}: {}'.format(self.invoice_number, self.title)

    def get_absolute_url(self):
        return '/invoice/view/{}/?key={}'.format(self.id, self.password)

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

    # settings:
    integrate_medical_aid = models.BooleanField(default=False)
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
        if self.status == 'paid': return True
        return (self.invoice_amount - self.amount_paid) == 0

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

class Payment(models.Model):

    def __str__(self):
        return "{} -> {}. {}".format(
            self.customer_id,
            self.practitioner_id,
            self.amount
        )

    practitioner_id = models.CharField(max_length=128, db_index=True)
    customer_id = models.CharField(max_length=128, db_index=True)

    invoice = models.ForeignKey(Invoice, blank=True, null=True)
    appointments = ArrayField(models.CharField(max_length=100, blank=True, null=True), default=[], db_index=True, blank=True, null=True)

    currency = models.CharField(max_length=4,blank=True, null=True, default='ZAR')
    amount = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)
    payment_method = models.CharField(max_length=128, choices=PAYMENT_METHODS, db_index=True)
    payment_date = models.DateTimeField(db_index=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

    @classmethod
    def from_invoice(cls, invoice, payment_method='unknown', with_save=True):

        # check for dupes:
        existing_payments = Payment.objects.filter(invoice=invoice)
        if existing_payments.count() > 0:
            print("Payment already exists")
            return existing_payments.first()

        payment = cls()
        copy_fields = ['practitioner_id', 'customer_id', 'appointments']
        for field in copy_fields:
            value = getattr(invoice, field)
            setattr(payment, field, value)

        payment.invoice_id = invoice.id
        payment.amount = invoice.amount_paid
        # payment.payment_date = invoice.modified_date
        payment.payment_date = invoice.created_date
        payment.payment_method = payment_method
        if with_save:
            payment.save()
        return payment


def proof_upload_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    filename_base, filename_ext = os.path.splitext(filename)
    # return 'practitioner/images/{}/profile{}'.format(instance.user_id, filename_ext)
    invoice = instance.invoice
    return 'proofs/{}/{}/filename_base{}'.format(invoice.practitioner_id, invoice.id, filename_ext)

class ProofOfPayment(models.Model):
    invoice = models.ForeignKey(Invoice)
    payment = models.ForeignKey(Payment, blank=True, null=True)
    document = models.FileField(upload_to=proof_upload_path, blank=True, null=True) # <- ideally this should really be required. Just for testing :()
    approved = models.BooleanField(default = False)

    medical_aid_email = models.EmailField(null=True, blank=True)
    auto_submit_to_medical_aid = models.BooleanField(default=False)

    def approve(self):
        self.approved = True
        self.save()
        payment = Payment.from_invoice(self.invoice)
        payment.proofofpayment_set.add(self)
        payment.save()
        if self.auto_submit_to_medical_aid:
            print('Send to medical aid: {}'.format(self.medical_aid_email))


# class Action(models.Model):
#     invoice = models.ForeignKey(Invoice, blank=True, null=True)
#     payment = models.ForeignKey(Payment, blank=True, null=True)
#     actor = models.CharField()

from .signals import *