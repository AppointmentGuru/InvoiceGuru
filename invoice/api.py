from rest_framework import routers, viewsets
from .models import Invoice
from .serializers import InvoiceSerializer
from django.db.models import Q


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

router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
