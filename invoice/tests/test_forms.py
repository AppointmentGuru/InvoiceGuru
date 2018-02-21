# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.urls import reverse
from django.test import TestCase

from ..forms import InvoiceConstructionForm

class InvoiceConstructionFormTestCase(TestCase):

    def setUp(self):
        self.form = InvoiceConstructionForm()

    def test_it_works(self):
        pass
        # if self.form.isValid():
        #     self.form.save()
