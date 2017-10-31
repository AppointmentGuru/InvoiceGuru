'''
Signals for Invoice model
'''
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Invoice
from dateutil.parser import parse
from decimal import Decimal
import random

@receiver(pre_save, sender=Invoice, dispatch_uid="invoice.signals.apply_context")
def apply_context(sender, instance, **kwargs):

    context = instance.context
    invoice_total = 0
    object_ids = instance.object_ids
    appointments = context.get('appointments', [])
    for appt in appointments:
        invoice_total += Decimal(appt.get('price', 0))

        appt_key = 'appointment:{}'.format(appt.get('id'))
        if appt_key not in object_ids:
            object_ids.append(appt_key)

    instance.invoice_amount = invoice_total
    instance.due_date = context.get('due_date')

    if instance.customer_id is None:
        instance.customer_id = context.get('customer_id')
    instance.object_ids = object_ids

    appointments_exist = (len(appointments) > 0)
    if instance.invoice_period_from is None and appointments_exist:
        instance.invoice_period_from = parse(appointments[0].get('start_time')).date()

    if instance.invoice_period_to is None and appointments_exist:
        instance.invoice_period_to = parse(appointments[-1].get('start_time')).date()

    # if instance.invoice_number is None:
    #     random_number = random.choice(range(1000,9999))
    #     instance.invoice_number = 'INV-{}-{}'.format(random_number, instance.customer_id)

    if instance.status == 'paid':
        instance.amount_paid = instance.invoice_amount

    # if instance.title is None:
    #     instance.title = instance.invoice_number
