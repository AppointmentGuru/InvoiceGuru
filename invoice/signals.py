'''
Signals for Invoice model
'''
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django_nosql.signals import (sync_readonly_db, SYNC_TYPE)

from .models import Invoice, ProofOfPayment, Transaction
from .invoicebuilder import InvoiceBuilder

from dateutil.parser import parse
from decimal import Decimal
import random

@receiver(pre_save, sender=Invoice, dispatch_uid="invoice.signals.apply_context")
def enrich_invoice(sender, instance, **kwargs):

    instance.enrich(save_context=False)
    instance.invoice_amount = instance.calculate_invoice_amount()

@receiver(post_save, sender=Invoice, dispatch_uid="invoice.signals.invoice_post_save_actions")
def invoice_post_save_actions(sender, instance, **kwargs):
    # create a transaction
    Transaction.from_invoice(instance, transaction_type='Invoice', with_save=True)
    due = Decimal(instance.amount_due)
    if instance.status == 'paid' and due > 0:
        Transaction.from_invoice(instance, transaction_type='Payment', amount=due, with_save=True)

@receiver(post_save, dispatch_uid="django_nosql.sync")
def nosql_sync(sender, instance, created, **kwargs):
    sync_readonly_db(instance, SYNC_TYPE.UPDATE, created)

@receiver(post_delete, dispatch_uid="django_nosql.sync.delete")
def sync_remove_readonly_db(sender, instance, **kwargs):
    sync_readonly_db(instance, SYNC_TYPE.DELETE)



