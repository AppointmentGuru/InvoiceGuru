from django.db import models

INVOICE_STATUSES = [
    ('new', 'new'),
    ('sent', 'sent'),
    ('paid', 'paid'),
    ('unpaid', 'unpaid'),
]

'''
curl -i https://invoice-generator.com \
  -d from="Invoiced, Inc.%0AVAT ID: 1234" \
  -d to="Jared%0AVAT ID: 4567" \
  -d logo="https://invoiced.com/img/logo-invoice.png" \
  -d number=1 \
  -d date="Feb 9, 2015" \
  -d payment_terms="Charged - Do Not Pay" \
  -d items[0][name]="Starter Plan Monthly" \
  -d items[0][quantity]=1 \
  -d items[0][unit_cost]=99 \
  -d items[1][name]="Starter Plan Monthly" \
  -d items[1][quantity]=1 \
  -d items[1][unit_cost]=99 \
  -d items[2][name]="Starter Plan Monthly" \
  -d items[2][quantity]=2 \
  -d items[2][unit_cost]=99 \
  -d tax_title="VAT" \
  -d fields[tax]="%" \
  -d tax=8 \
  -d currency="ZAR" \
  -d notes="Thanks for being an awesome customer!" \
  -d terms="No need to submit payment. You will be auto-billed for this invoice." \
> invoice.vat.pdf && open invoice.vat.pdf
'''

class Invoice(models.Model):

    status = models.CharField(max_length=10, choices=INVOICE_STATUSES, default='new')

    from_id = models.CharField(max_length=36,blank=True, null=True)
    to_id = models.CharField(max_length=36,blank=True, null=True)
    invoice_number = models.CharField(max_length=36,blank=True, null=True) # auto-generate if not provided
    purchase_order_number = models.CharField(max_length=36,blank=True, null=True)

    logo = models.URLField(blank=True, null=True)

    from_string = models.TextField(blank=True, null=True)
    to_string = models.TextField(blank=True, null=True)

    currency = models.CharField(max_length=4,blank=True, null=True, default='ZAR')
    discount = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    tax = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    shipping = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    amount_paid = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    date = models.DateField(auto_now_add = True, db_index=True)
    due_date = models.DateField(blank=True, null=True, db_index=True)

    notes = models.TextField(blank=True, null=True)
    terms = models.TextField(blank=True, null=True)

    created_date = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_date = models.DateTimeField(auto_now=True, db_index=True)


class LineItem(models.Model):

    invoice = models.ForeignKey('Invoice', related_name='invoice')

    name = models.CharField(max_length=36,blank=True, null=True)
    quantity = models.DecimalField(decimal_places=2, max_digits=10, default=0)
    cost = models.DecimalField(decimal_places=2, max_digits=10, default=0)

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)


from .signals import *