# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-16 08:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('raster', '0002_site'),
    ]

    operations = [
        migrations.CreateModel(
            name='SourceRaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daterun', models.DateField()),
                ('pol', models.CharField(max_length=10)),
                ('ech', models.IntegerField()),
                ('type', models.CharField(max_length=10)),
            ],
        ),
        migrations.DeleteModel(
            name='Site',
        ),
    ]