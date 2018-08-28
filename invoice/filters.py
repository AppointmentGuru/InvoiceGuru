'''
Filters for use with Invoices
'''
from .models import Invoice, Transaction
from django_filters.rest_framework import FilterSet
from rest_framework.filters import BaseFilterBackend
import django_filters

class InvoiceFilter(FilterSet):
    	# time needs to be in the format: 2016-10-17 11:34:51
    after_utc = django_filters.DateFilter(name="date", lookup_expr='gte')
    before_utc = django_filters.DateFilter(name="date", lookup_expr='lte')
    # status_in = todo ..

    class Meta:
        model = Invoice
        fields = ['practitioner_id', 'date', 'customer_id']

class IdsInFilter(BaseFilterBackend):
    """
    Filter that only allows users to see their own objects.
    """
    def filter_queryset(self, request, queryset, view):
        ids_string = request.GET.get('ids')
        if ids_string is not None:
            ids = ids_string.split(',')
            if len(ids) > 0:
                queryset = queryset.filter(id__in=ids)
        return queryset

class TransactionFilter(FilterSet):
    	# time needs to be in the format: 2016-10-17 11:34:51
    after_utc = django_filters.DateFilter(name="date__date", lookup_expr='gte')
    before_utc = django_filters.DateFilter(name="date__date", lookup_expr='lte')

    # status_in = todo ..

    class Meta:
        model = Transaction
        fields = ['practitioner_id', 'date', 'customer_id']

