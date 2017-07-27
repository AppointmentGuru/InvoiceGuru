from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .tasks import generate_pdf, generate_invoice_number

from .models import Invoice

@receiver(post_save, sender=Invoice, dispatch_uid="schedule.signals.invoice_created")
def invoice_created(sender, instance, created, **kwargs):

    if instance.invoice_number is None:
        instance.invoice_number = generate_invoice_number(instance)

    # pdf = generate_pdf(instance)
    # instance.save()

