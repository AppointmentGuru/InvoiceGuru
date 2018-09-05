# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-08-27 09:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('invoice', '0029_auto_20180731_0811'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='billing_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='date',
            field=models.DateField(blank=True, db_index=True, default=django.utils.timezone.localdate, null=True),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='template',
            field=models.CharField(blank=True, choices=[('basic', 'basic - A simple invoice template'), ('basic_v2', 'basic_v2 - Version 2 of the simple invoice template')], default='basic_v2', max_length=255, null=True),
        ),
    ]