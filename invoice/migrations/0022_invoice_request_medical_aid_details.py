# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-06-27 14:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0021_auto_20180627_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='request_medical_aid_details',
            field=models.BooleanField(default=False),
        ),
    ]
