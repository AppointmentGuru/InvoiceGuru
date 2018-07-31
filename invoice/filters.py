'''
Filters for use with Invoices
'''
from .models import Invoice, Transaction
from django_filters.rest_framework import FilterSet
import django_filters

class InvoiceFilter(FilterSet):
    	# time needs to be in the format: 2016-10-17 11:34:51
    after_utc = django_filters.DateFilter(name="date", lookup_expr='gte')
    before_utc = django_filters.DateFilter(name="date", lookup_expr='lte')

    # status_in = todo ..

    class Meta:
        model = Invoice
        fields = ['practitioner_id', 'date', 'customer_id']

class TransactionFilter(FilterSet):
    	# time needs to be in the format: 2016-10-17 11:34:51
    after_utc = django_filters.DateFilter(name="date", lookup_expr='gte')
    before_utc = django_filters.DateFilter(name="date", lookup_expr='lte')

    # status_in = todo ..

    class Meta:
        model = Transaction
        fields = ['practitioner_id', 'date', 'customer_id']

