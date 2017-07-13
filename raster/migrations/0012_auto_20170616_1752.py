# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-16 15:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('raster', '0011_auto_20170616_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='type_source_raster',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='raster.TypeSourceRaster'),
        ),
        migrations.AlterField(
            model_name='source',
            name='url',
            field=models.CharField(default='', max_length=200),
        ),
    ]
