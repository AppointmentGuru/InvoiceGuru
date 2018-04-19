# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-19 13:12
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0014_auto_20180419_1306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='appointments',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, max_length=100, null=True), blank=True, db_index=True, default=[], null=True, size=None),
        ),
    ]
