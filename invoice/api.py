'''
InvoiceGuru API
'''
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.conf import settings

from .mixins import MultiSerializerMixin
from .filters import (
    InvoiceFilter,
    TransactionFilter,
    IdsInFilter,
    OwnerFilterBackend
)
from .serializers import (
    InvoiceSerializer,
    InvoiceSettingsSerializer,
    InvoiceListViewSerializer,
    TransactionSerializer
)
from .models import (
    Invoice,
    InvoiceSettings,
    Transaction
)

from rest_framework import (
    routers,
    viewsets,
    decorators,
    response,
    status,
    filters,
    permissions
)

from .tasks import (
    mark_invoice_as_paid,
    send_invoice_or_receipt
)

class Guru:

    services = {
        'appointmentguru': settings.APPOINTMENTGURU_API,
        'medicalaidguru': settings.MEDICALAIDGURU_API,
    }
    def __init__(self, service, authenticated_user_id):
        self.base_url = self.services.get(service)
        self.headers = {
            'X_ANONYMOUS_CONSUMER': 'false',
            'X_AUTHENTICATED_USERID': str(authenticated_user_id),
        }

class InvoiceSettingsViewSet(viewsets.ModelViewSet):
    queryset = InvoiceSettings.objects.all()
    serializer_class = InvoiceSettingsSerializer
    filter_backends = (OwnerFilterBackend,)

    def get_object(self):
        user = self.request.user
        queryset = self.get_queryset()
        return get_object_or_404(queryset, practitioner_id=user.id)


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = TransactionFilter
    ordering_fields = ('date', 'customer_id', 'practitioner_id', 'amount',)
    ordering = ('-date',)

    def get_queryset(self):
        user = self.request.user
        return Transaction.objects.filter(practitioner_id=user.id)

class InvoiceViewSet(MultiSerializerMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    filter_backends = (
        DjangoFilterBackend,
        filters.OrderingFilter,
        filters.SearchFilter,
        IdsInFilter
    )
    filter_class = InvoiceFilter
    ordering_fields = ('date', 'due_date', 'id', 'date_created', 'invoice_amount')
    search_fields = ('date', 'due_date', 'sender_email', 'title', 'invoice_amount', 'invoicee_details', 'medicalaid_details',)
    ordering = ('-date',)

    default_serializer_class = InvoiceSerializer
    serializer_map = {
        'list': InvoiceListViewSerializer
    }


    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(
            Q(practitioner_id=user.id) |
            Q(customer_id=user.id)
            )

    # @decorators.detail_route(methods=['post'])
    # def appointments(self, request, pk=None):
    #     '''
    #     Send a list of appointment_ids and we add the full context to the invoice
    #     '''
    #     invoice = get_object_or_404(Invoice, pk=pk, practitioner_id=request.user.id)
    #     appointments = request.data.get('appointments', [])
    #     appointment_ids = appointments.split(',')

    #     # appointments = fetch_appointments(invoice.practitioner_id, appointment_ids)
    #     api = get_mirco("appointmentguru", request.user.id)
    #     api.list("appointments", params={"ids": })
    #     invoice.context.update({
    #         'appointments': appointments
    #     })
    #     invoice.save()
    #     data = InvoiceSerializer(invoice).data
    #     return response.Response(data)

    @decorators.detail_route(methods=['post', 'get'])
    def send(self, request, pk):
        invoice = Invoice.objects.get(id=pk)

        to_email = request.data.get('to_email', None)
        to_emails = None
        if to_email is not None:
            to_emails = to_email.split(',')

        to_phone = request.data.get('to_phone', None)
        # update the status of all appointments
        data = {
            "from_email": invoice.sender_email,
            "to_emails": to_emails,
            "to_phone_numbers": [to_phone],
            "to_channels": [
                "practitioner:{}".format(request.user.id),
                "customer:{}".format(invoice.customer_id),
                "thread-practitioner:{}-client:{}".format(request.user.id, invoice.customer_id),
                "invoice:{}".format(invoice.id),
                "to:{}".format(to_phone)
            ],
            "invoice_id": invoice.id
        }
        send_result = send_invoice_or_receipt(data)
        print(send_result)
        if invoice.status != 'paid':
            invoice.status = 'sent'
            invoice.save()
        # send email to customer

        data = InvoiceSerializer(invoice).data

        return response.Response(data)

    @decorators.detail_route(methods=['post', 'get'])
    def paid(self, request, pk):
        '''
        Mark an invoice as paid
        '''
        send_receipt = request.data.get('send_receipt', False)
        payload = {
            "invoice_id": pk,
            "options": {
                "send_receipt": send_receipt
            }
        }
        invoice = mark_invoice_as_paid(payload)
        data = invoice._get_serialized()
        return response.Response(data)

class ReportsViewSet(viewsets.ViewSet):
    """
    A viewset for getting customized views for reports
    """

    @decorators.list_route(methods=['get'])
    def overdue(self, request):

        filters = {
            "practitioner_id": request.user.id
        }
        customer_id = request.GET.get('customer_id', None)
        if customer_id is not None:
            filters.update({
                "customer_id": customer_id
            })
        data = {
            "thirty": InvoiceListViewSerializer(Invoice.past_due(0, 30, other_filters=filters), many=True).data,
            "sixty": InvoiceListViewSerializer(Invoice.past_due(30, 60, other_filters=filters), many=True).data,
            "ninety": InvoiceListViewSerializer(Invoice.past_due(60, 90, other_filters=filters), many=True).data,
            # "older": InvoiceListViewSerializer(Invoice.past_due(90, other_filters=filters), many=True).data
        }

        return response.Response(data)

class BulkInvoiceViewSet(viewsets.ModelViewSet):
    '''
    Perform bulk action against a list of invoices
    '''
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(practitioner_id=user.id)

    @decorators.list_route(methods=['get', 'post'])
    def generate(self, request):
        pass

router = routers.DefaultRouter()
router.register(r'invoices/settings', InvoiceSettingsViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoices/reports', ReportsViewSet, base_name='reports')
router.register(r'invoices/bulk', BulkInvoiceViewSet, base_name='bulk-invoices')