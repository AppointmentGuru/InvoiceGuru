from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField, JSONField

INVOICE_STATUSES = [
    ('new', 'new'),
    ('sent', 'sent'),
    ('paid', 'paid'),
    ('unpaid', 'unpaid'),
]

TEMPLATES = [(key, '{} - {}'.format(key, values.get('title'))) for key, values in settings.TEMPLATE_REGISTRY.items()]

"""
class InvoiceSettings(models.Model):

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name =  models.CharField(max_length=255, blank=True, null=True)

    # configs:
    template = models.CharField(max_length=255, blank=True, null=True, help_text='The base template to use for invoices using these settings')
"""

class Invoice(models.Model):

    # relationships
    practitioner_id = models.CharField(max_length=128, db_index=True)
    customer_id = models.CharField(max_length=128, db_index=True)
    object_ids = ArrayField(models.CharField(max_length=100), default=[], db_index=True)

    title = models.CharField(max_length=255,blank=True, null=True)
    status = models.CharField(max_length=10, choices=INVOICE_STATUSES, default='new', db_index=True)

    context = JSONField(default={})
    template = models.CharField(max_length=255,blank=True, null=True)

    currency = models.CharField(max_length=4,blank=True, null=True, default='ZAR')
    invoice_amount = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=10, default=0, db_index=True)

    date = models.DateField(auto_now_add = True, db_index=True)
    due_date = models.DateField(blank=True, null=True, db_index=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)

from .signals import *