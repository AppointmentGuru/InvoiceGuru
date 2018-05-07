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
    invoice_amount_paid = 0
    object_ids = instance.object_ids
    appointments = context.get('appointments', [])

    for appt in appointments:

        codes = appt.get('codes',[])
        if len(codes) > 0:
            li_total = sum([Decimal(code.get('price')) for code in codes])
            if appt['price'] != li_total:
                appt['price'] = str(li_total)

        appt_price = Decimal(appt.get('price', 0))
        amount_paid = Decimal(appt.get('amount_paid', 0))
        appt_is_paid = appt.get('status') == 'P'
        if appt_is_paid:
            amount_paid = appt_price
            # if status is paid, make sure this reflects in amount_paid
            appt.update({"amount_paid": int(amount_paid)})
        subtotal = appt_price - amount_paid

        invoice_amount_paid += amount_paid
        invoice_total += appt_price

        appt_key = 'appointment:{}'.format(appt.get('id'))
        if appt_key not in object_ids:
            object_ids.append(appt_key)

    # only automatically set amount paid if it's greater than zero so as not to override
    # explicitly set amount paid
    if invoice_amount_paid > 0:
        instance.amount_paid = invoice_amount_paid

    instance.invoice_amount = invoice_total
    instance.due_date = context.get('due_date')
    instance.date = context.get('date')

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
