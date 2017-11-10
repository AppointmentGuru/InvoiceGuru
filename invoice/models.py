from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField
import uuid

INVOICE_STATUSES = [
    ('new', 'new'),
    ('sent', 'sent'),
    ('paid', 'paid'),
    ('unpaid', 'unpaid'),
]

TEMPLATES = [(key, '{} - {}'.format(key, values.get('title'))) for key, values in settings.TEMPLATE_REGISTRY.items()]

def get_uuid():
  return str(uuid.uuid4())


"""
class InvoiceSettings(models.Model):

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name =  models.CharField(max_length=255, blank=True, null=True)

    # configs:
    template = models.CharField(max_length=255, blank=True, null=True, help_text='The base template to use for invoices using these settings')
"""

class Invoice(models.Model):

    def __str__(self):
        return '#{}: {}'.format(self.invoice_number, self.title)

    # relationships
    practitioner_id = models.CharField(max_length=128, db_index=True)
    customer_id = models.CharField(max_length=128, db_index=True)
    object_ids = ArrayField(models.CharField(max_length=100), default=[], db_index=True)
    sender_email = models.EmailField(default='support@appointmentguru.co')
    # invoice_number = models.CharField(max_length=255,blank=True, null=True)
    title = models.CharField(max_length=255,blank=True, null=True)
    status = models.CharField(max_length=10, choices=INVOICE_STATUSES, default='new', db_index=True)

    context = JSONField(default={})
    template = models.CharField(max_length=255, blank=True, null=True, choices=TEMPLATES, default='basic')

    password = models.CharField(max_length=255, blank=True, null=True, default=get_uuid)
    customer_password = models.CharField(max_length=255, blank=True, null=True, default=get_uuid)

    currency = models.CharField(max_length=4,blank=True, null=True, default='ZAR')
    invoice_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)

    date = models.DateField(auto_now_add = True, db_index=True)
    due_date = models.DateField(blank=True, null=True, db_index=True)

    invoice_period_from = models.DateField(db_index=True, blank=True, null=True)
    invoice_period_to = models.DateField(db_index=True, blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

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

from .signals import *