"""
Class for migrating an invoice from version 1 -> version 2
"""
class InvoiceMigrator:

    def __init__(self, invoice):
        self.invoice = invoice

    def populate_appointments_from_context(self):
        appointments = self.invoice.context.get('appointments',[])
        self.invoice.appointments = [appt.get('id') for appt in appointments]
        self.invoice.save()