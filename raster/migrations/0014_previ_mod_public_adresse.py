# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-28 14:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raster', '0013_auto_20180328_1511'),
    ]

    operations = [
        migrations.AddField(
            model_name='previ_mod',
            name='public_adresse',
            field=models.CharField(default='', max_length=200),
        ),
    ]