from .models import Invoice

class InvoiceFilter(filters.FilterSet):
    	# time needs to be in the format: 2016-10-17 11:34:51
    after_utc = django_filters.DateFilter(name="date", lookup_expr='gte')
    before_utc = django_filters.DateFilter(name="date", lookup_expr='lte')

    # status_in = todo ..

    class Meta:
        model = Invoice
        fields = ['practitioner_id', 'practitioner_id', 'invoice_number', 'date', 'due_date']

