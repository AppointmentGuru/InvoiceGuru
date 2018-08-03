from django.contrib import admin
from .models import Invoice, InvoiceSettings, Transaction, ProofOfPayment

class TransactionInline(admin.TabularInline):
    model = Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('practitioner_id', 'customer_id', 'date', 'type', 'invoice', 'currency', 'amount',)
    list_filter = ('practitioner_id', 'method', )


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'practitioner_id', 'customer_id', 'sender_email', 'date', 'due_date', 'currency', 'invoice_amount', 'amount_paid', 'status')
    list_filter = ('practitioner_id', 'status',)
    inlines = [TransactionInline]

class InvoiceSettingsAdmin(admin.ModelAdmin):
    list_display = ('id',
        'practitioner_id',
        'quote_notes',
        'invoice_notes',
        'receipt_notes',
        'billing_address',
        'customer_info',
        'lineitem_template',
        'include_booking_info',
        'integrate_medical_aid',
        'show_snapcode_on_invoice',
        'allow_pre_payments',
        'allow_submit_to_medical_aid',
        'include_vat',
        'snap_id',
        'vat_percent'
    )

admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(InvoiceSettings, InvoiceSettingsAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(ProofOfPayment)