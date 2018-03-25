'''
InvoiceGuru API
'''
from rest_framework import routers, viewsets, decorators, response, status, filters

from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.conf import settings

from .models import Invoice
from .serializers import InvoiceSerializer
from .guru import send_invoice, publish
from .helpers import to_context, fetch_data, fetch_appointments
from .filters import InvoiceFilter

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


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter,)
    filter_class = InvoiceFilter
    ordering_fields = ('date', 'due_date', 'id', 'date_created', 'invoice_amount')
    ordering = ('-date',)

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(
            Q(practitioner_id=user.id) |
            Q(customer_id=user.id)
        )

    @decorators.list_route(methods=['get', 'post'])
    def construct(self, request):
        '''
        Given a practitioner_id, list of appointments, and customer_id, construct an invoice context
        TODO: move this into POST /invoice
        '''
        practitioner_id = request.GET.get('practitioner_id')
        appointment_ids = request.GET.get('appointment_ids', '').split(',')
        client_id = request.GET.get('client_id')
        default_context = request.data.get('context', {})
        practitioner, appointments, medical_record = fetch_data(practitioner_id, appointment_ids, client_id)

        invoice = Invoice()
        invoice.practitioner_id = practitioner_id
        invoice.customer_id = client_id
        invoice.appointment_ids = appointment_ids
        context = invoice.get_context(default_context=default_context)

        data = { "context": invoice.context }
        result_code = status.HTTP_200_OK
        if request.method == 'POST':
            extra_fields = ['practitioner_id', 'customer_id',
                            'title', 'invoice_period_from', 'invoice_period_to',
                            'sender_email', 'date', 'due_date', 'status']
            for field in extra_fields:
                value = context.get(field, None)
                if value is not None:
                    setattr(invoice, field, value)

            invoice.save()
            data['id'] = invoice.id
            data['password'] = invoice.password
            result_code = status.HTTP_201_CREATED

        return response.Response(data, status=result_code)

    @decorators.detail_route(methods=['post'])
    def appointments(self, request, pk=None):
        '''
        Send a list of appointment_ids and we add the full context to the invoice
        '''
        invoice = get_object_or_404(Invoice, pk=pk, practitioner_id=request.user.id)
        appointments = request.data.get('appointments', [])
        appointment_ids = appointments.split(',')

        appointments = fetch_appointments(invoice.practitioner_id, appointment_ids)

        invoice.context.update({
            'appointments': appointments
        })
        invoice.save()
        data = InvoiceSerializer(invoice).data
        return response.Response(data)

    @decorators.detail_route(methods=['post', 'get'])
    def send(self, request, pk):
        invoice = Invoice.objects.get(id=pk)

        to_email = request.data.get('to_email', None)
        to_emails = None
        if to_email is not None:
            to_emails = to_email.split(',')

        to_phone = request.data.get('to_phone', None)
        # update the status of all appointments
        # update invoice status
        send_result = send_invoice(
            invoice,
            to_emails=to_emails,
            to_phone=to_phone)
        print(send_result)
        if invoice.status != 'paid':
            invoice.status = 'sent'
            invoice.save()
        # send email to customer

        data = InvoiceSerializer(invoice).data

        summarized = [{"id": appt.get('id')} \
                        for appt \
                        in data.get('context',{}).get('appointments')]
        data.update({"context": { "appointments": summarized } })

        publish(settings.PUBLISHKEYS.invoice_sent, data)
        return response.Response(data)

    @decorators.detail_route(methods=['post', 'get'])
    def paid(self, request, pk):
        '''
        Mark an invoice as paid
        '''

        invoice = Invoice.objects.get(id=pk)
        invoice.amount_paid = invoice.invoice_amount
        invoice.status = 'paid'
        invoice.save()

        data = InvoiceSerializer(invoice).data

        # shorten the data:
        summarized = [{"id": appt.get('id')} \
                        for appt \
                        in data.get('context',{}).get('appointments')]
        data.update({"context": { "appointments": summarized } })

        publish(settings.PUBLISHKEYS.invoice_paid, data)
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
router.register(r'invoices', InvoiceViewSet)
router.register(r'invoices/bulk', BulkInvoiceViewSet, base_name='bulk-invoices')
