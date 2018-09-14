"""
Class for migrating an invoice from version 1 -> version 2
"""
from .invoicebuilder import InvoiceBuilder

class InvoiceMigrator:
    """
from invoice.invoicemigrator import InvoiceMigrator
from invoice.models import Invoice
inv = Invoice.objects.get(id=3466)
mig = InvoiceMigrator(inv)
mig.upgrade()
    """

    def __init__(self, invoice):
        self.invoice = invoice

    def upgrade(self):
        '''
        Upgrade invoice to new version
        '''
        self.populate_appointments_from_context()
        InvoiceBuilder(self.invoice).enrich(with_save=True)
        # self.populate_client()
        # self.populate_practitioner()
        # self.populate_record()

    # def get_from_appointments(self, field):
    #     appointments = self.invoice.context.get('appointments',[])
    #     if len(appointments) > 0:
    #         appointment = appointments[0]
    #         return appointment.get(field)
    #     return None

    # def populate_practitioner(self):
    #     self.invoice.practitioner_data = self.get_from_appointments('practitioner')

    # def populate_client(self):
    #     self.invoice.client_data = self.get_from_appointments('client')

    # def populate_record(self):
    #     self.invoice.record_data = self.invoice.context.get('record')

    def populate_appointments_from_context(self):
        appointments = self.invoice.context.get('appointments',[])
        self.invoice.appointment_data = appointments
        self.invoice.appointments = [appt.get('id') for appt in appointments]
        self.invoice.save()