from django.contrib import admin
from .models import Invoice, InvoiceSettings, Payment, ProofOfPayment

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'practitioner_id', 'customer_id', 'date', 'due_date', 'currency', 'invoice_amount', 'amount_paid', 'status')
    list_filter = ('status', 'practitioner_id', )

admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceSettings)
admin.site.register(Payment)
admin.site.register(ProofOfPayment)