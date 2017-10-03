from rest_framework import routers, viewsets, decorators, response
from .models import Invoice
from .serializers import InvoiceSerializer
from .guru import send_invoice, publish
from django.db.models import Q
from django.conf import settings

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


router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
