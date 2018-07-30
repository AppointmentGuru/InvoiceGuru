'''
Filters for use with Invoices
'''
from .models import Invoice, Payment
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


def filter_transaction_invoices(request):

    customer_id = request.query_params.get('customer_id')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    query = {
        "practitioner_id": request.user.id
    }
    if customer_id is not None:
        query['customer_id'] = request.query_params.get('customer_id')
    if date_from is not None:
        query['date__gte'] = date_from
    if date_to is not None:
        query['date__lte'] = date_to
    return Invoice.objects.filter(**query).order_by('date')

def filter_payments(request):
    
    customer_id = request.query_params.get('customer_id')
    date_from = request.query_params.get('date_from')
    date_to = request.query_params.get('date_to')
    query = {
        "practitioner_id": request.user.id
    }
    if customer_id is not None:
        query['customer_id'] = request.query_params.get('customer_id')
    if date_from is not None:
        query['payment_date__gte'] = date_from
    if date_to is not None:
        query['payment_date__lte'] = date_to
    return Payment.objects.filter(**query).order_by('date')


