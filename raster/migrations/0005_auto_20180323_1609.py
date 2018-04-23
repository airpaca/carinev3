# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2018-03-23 15:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('raster', '0004_auto_20180323_1127'),
    ]

    operations = [
        migrations.CreateModel(
            name='OutputData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desc', models.CharField(default='', max_length=200)),
                ('dir', models.CharField(default='', max_length=200)),
            ],
        ),
        migrations.AddField(
            model_name='dicopath',
            name='ext',
            field=models.CharField(default='', max_length=10),
        ),
        migrations.AddField(
            model_name='dicopath',
            name='sep',
            field=models.CharField(default='', max_length=1),
        ),
        migrations.AddField(
            model_name='previ_mod',
            name='output_dir',
            field=models.CharField(default='/var/www/html/', max_length=200),
        ),
        migrations.AddField(
            model_name='remotemachine',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='outputdata',
            name='type',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='raster.DicoPath'),
        ),
    ]
