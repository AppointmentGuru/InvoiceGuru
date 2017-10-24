'''
InvoiceGuru API
'''
from rest_framework import routers, viewsets, decorators, response, status

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
        self.headers = headers = {
            'X_ANONYMOUS_CONSUMER': 'false',
            'X_AUTHENTICATED_USERID': str(authenticated_user_id),
        }

    '''
    def call(self, verb, path, data):
        url = '{}/api/practitioners/{}/'.format(settings.APPOINTMENTGURU_API, practitioner_id)
    '''


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    ordering = ['-id',]

    filter_backends = (DjangoFilterBackend,)
    filter_class = InvoiceFilter

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
        '''
        practitioner_id = request.GET.get('practitioner_id')
        appointment_ids = request.GET.get('appointment_ids', '').split(',')
        client_id = request.GET.get('client_id')
        default_context = request.data.get('context', {})
        practitioner, appointments, medical_record = fetch_data(practitioner_id, appointment_ids, client_id)

        context = to_context(
                    practitioner,
                    appointments,
                    medical_record,
                    default_context=default_context,
                    format_times = False)
        data = {
            "context": context,
        }
        result_code = status.HTTP_200_OK
        if request.method == 'POST':
            invoice = Invoice()
            invoice.context = context

            extra_fields = ['title', 'invoice_period_from', 'invoice_period_to', 'date', 'due_date']
            for field in extra_fields:
                value = context.get(field, None)
                if value is not None:
                    setattr(invoice, field, value)

            invoice.save()
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

        to_email = request.data.get('to_email')
        # update the status of all appointments
        # update invoice status
        send_invoice(invoice, to_email)
        invoice.status = 'sent'
        invoice.save()
        # send email to customer

        data = InvoiceSerializer(invoice).data
        publish(settings.PUBLISHKEYS.invoice_sent, data)
        return response.Response(data)

    @decorators.detail_route(methods=['post', 'get'])
    def paid(self, request, pk):

        invoice = Invoice.objects.get(id=pk)
        invoice.status = 'paid'
        invoice.save()

        data = InvoiceSerializer(invoice).data
        publish(settings.PUBLISHKEYS.invoice_paid, data)
        return response.Response(data)


router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
