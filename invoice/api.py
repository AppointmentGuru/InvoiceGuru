from rest_framework import routers, viewsets, decorators, response
from .models import Invoice
from .serializers import InvoiceSerializer
from .guru import send_invoice, publish
from django.db.models import Q
from django.conf import settings
import requests, json

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

    def get_queryset(self):
        user = self.request.user
        return Invoice.objects.filter(
            Q(practitioner_id=user.id) |
            Q(customer_id=user.id)
        )

    @decorators.list_route(methods=['get'])
    def construct(self, request):
        '''
        Given a practitioner_id, list of appointments, and customer_id, construct an invoice context
        '''
        practitioner_id = request.GET.get('practitioner_id')
        appointment_ids = request.GET.get('appointment_ids', '').split(',')
        client_id = request.GET.get('client_id')
        headers = {
            'X_ANONYMOUS_CONSUMER': 'false',
            'X_AUTHENTICATED_USERID': str(practitioner_id),
        }

        # getme:
        url = '{}/api/practitioners/{}/'.format(settings.APPOINTMENTGURU_API, practitioner_id)
        practitioner = requests.get(url, headers=headers).json()

        appointments = []
        for appointment_id in appointment_ids:
            url = '{}/api/appointments/{}/'.format(settings.APPOINTMENTGURU_API, appointment_id)
            print(url)
            result = requests.get(url, headers=headers)
            print(result)
            if result.status_code == 200:
                appointments.append(result.json())

        url = '{}/records/{}'.format(settings.MEDICALAIDGURU_API, client_id)
        record_request = requests.get(url, headers=headers)
        medical_record = {}
        if record_request.status_code == 200:
            medical_record = record_request.json()
        data = {
            "practitioner": practitioner,
            "appointments": appointments,
            "record": medical_record
        }

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
