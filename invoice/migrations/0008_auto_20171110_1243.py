# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-10 12:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0007_invoice_customer_password'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='invoice',
            name='invoice_number',
        ),
        migrations.AddField(
            model_name='invoice',
            name='sender_email',
            field=models.EmailField(default='support@appointmentguru.co', max_length=254),
        ),
    ]
