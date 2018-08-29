from django.db.models import Sum
from django.conf import settings

from datetime import datetime
from decimal import Decimal

from .invoicebuilder import InvoiceBuilder
from .guru import publish
import requests

class MultiSerializerMixin():
    '''
    A mixins that allows you to easily specify different serializers for various verbs
    '''

    def get_serializer_class(self):
        default_serializer = self.default_serializer_class
        return self.serializer_map.get(self.action, default_serializer)


class InvoiceModelMixin:

    cached_settings = None

    def get_absolute_url(self):
        return '/invoice/view/{}/?key={}'.format(self.id, self.password)

    def get_short_url(self, force=False, admin_url=True):
        '''
        curl https://www.googleapis.com/urlshortener/v1/url?key=... \
            -H 'Content-Type: application/json' \
            -d '{"longUrl": "https://google.com"}'
        '''
        url = 'https://www.googleapis.com/urlshortener/v1/url'
        params = {
            "key": settings.GOOGLE_API_SHORTENER_TOKEN
        }

        if admin_url:
            url_to_shorten = self.admin_invoice_url
        else:
            url_to_shorten = self.customer_invoice_url

        result = requests.post(
            url,
            json={'longUrl': url_to_shorten},
            params=params)
        short_url = result.json().get('id')
        self.short_url = short_url
        self.save()
        return short_url

    def __get_snap_url(self, is_qr_code=True):
        base = "https://pos.snapscan.io/qr/"
        snap_id = self.settings.snap_id
        if is_qr_code:
            snap_id = "{}.svg".format(snap_id)
        snap_params = "?invoice_id={}&amount={}".format(
            self.id,
            self.amount_due.replace('.', '')
        )
        return "{}{}{}&strict=true".format(
            base,
            snap_id,
            snap_params
        )

    def __get_client(self):
        return self.client_data

    @property
    def get_client_email(self):
        return self.__get_client().get("email")

    @property
    def get_client_full_name(self):
        fname = self.__get_client().get("first_name")
        lname = self.__get_client().get("last_name")
        return "{} {}".format(fname, lname)

    @property
    def get_client_phone_number(self):
        return self.__get_client().get("phone_number")

    @property
    def get_download_url(self):
        return '/invoice/{}/?key={}'.format(self.id, self.password)

    @property
    def get_view_url(self):
        return '/invoice/view/{}/?key={}'.format(self.id, self.password)

    @property
    def calculated_amount_paid(self):
        from .models import Transaction
        total = Transaction.objects \
            .filter(invoice = self, type='Payment')\
            .aggregate(amount_paid = Sum('amount'))\
            .get('amount_paid', Decimal(0))

        if total is None: total = Decimal(0)
        return total

    @property
    def amount_due(self):
        due = Decimal(self.invoice_amount) - Decimal(self.calculated_amount_paid)
        due = max(Decimal(0), due)
        return format(due, '.2f')

    @property
    def show_snapcode_on_invoice(self):
        return self.settings.show_snapcode_on_invoice

    @property
    def get_snapscan_url(self):
        return self.__get_snap_url(is_qr_code=False)

    @property
    def get_snapscan_qr(self):
        return self.__get_snap_url(is_qr_code=True)

    @property
    def is_receipt(self):
        return self.status == 'paid'
        # return (self.invoice_amount - self.amount_paid) == 0

    @property
    def invoice_number(self):
        if self.title is None: return 'INV-{}'.format(self.id)
        initials = ("").join([word[0:1].upper() for word in self.title.split(' ') if word.isalpha()])
        return '{}-{}'.format(initials, self.id)

    @property
    def admin_invoice_url(self):
        base = settings.INVOICEGURU_BASE_URL
        return '{}/invoice/{}?key={}'.format(base, self.pk, self.password)

    @property
    def customer_invoice_url(self):
        base = settings.INVOICEGURU_BASE_URL
        return '{}/invoice/{}?key={}'.format(base, self.pk, self.customer_password)

    @property
    def settings(self):
        from .models import InvoiceSettings

        if self.cached_settings is not None:
            return self.cached_settings
        try:
            settings = InvoiceSettings.objects.get(practitioner_id = self.practitioner_id)
            self.cached_settings = settings
            return settings
        except InvoiceSettings.DoesNotExist:
            return None

    def enrich(self, with_save=False):
        return InvoiceBuilder(self).enrich(with_save=False)

    def calculate_invoice_amount(self, with_save=False):
        appointments = self.appointment_data
        invoice_total = Decimal(0)
        for appointment in appointments:
            price = appointment.get('price', 0)
            invoice_total += Decimal(price)
        self.invoice_amount = invoice_total
        if with_save:
            self.save()
        return self.invoice_amount

    def _get_serialized(self):
        from .serializers import InvoiceSerializer
        if isinstance(self.date, datetime):
            self.date = self.date.date() # make sure date is only a date
        return InvoiceSerializer(self).data

    def _get_payload(self):
        data = self._get_serialized()
        summarized = [{"id": appt.get('id')} \
                    for appt \
                    in data.get('context',{}).get('appointments')]
        data.update({"context": { "appointments": summarized } })
        return data

    def send(self, to_email=False, to_phone=False, to_inapp = False):

        from .tasks import send_invoice_or_receipt
        data = {
            "from_email": self.sender_email,
            "invoice_id": self.id
        }
        if to_email and self.get_client_email:
            data.update({
                "to_emails": [self.get_client_email]
            })
        if to_phone and self.get_client_phone_number:
            data.update({
                "to_phone_numbers": [self.get_client_phone_number]
            })
        if to_inapp and self.get_client_phone_number:
            data.update({
                "to_channels": [self.get_client_phone_number]
            })
        return send_invoice_or_receipt(data)

    def send_to_medical_aid(self):
        pass

    def publish(self):
        if self.status == 'paid':
            self.publish_paid()
        if self.status == 'sent':
            self.publish_sent()

    def publish_paid(self):
        data = self._get_payload()
        publish(settings.PUBLISHKEYS.invoice_paid, data)

    def publish_sent(self):
        data = self._get_payload()
        publish(settings.PUBLISHKEYS.invoice_sent, data)

