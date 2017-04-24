from rest_framework import routers, serializers, viewsets
from .models import Invoice, LineItem

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
