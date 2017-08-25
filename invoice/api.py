from rest_framework import routers, serializers, viewsets
from .models import Invoice

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['practitioner_id', 'customer_id', 'title', 'status', 'context', 'template']


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    # def get_queryset(self):

        # user = self.request.user
        # TODO: return the list of default settings if the user has not
        # provided custom communications
        # return CustomProcessSetting.objects.filter(practitioner=user)


router = routers.DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
