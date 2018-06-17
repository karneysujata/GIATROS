# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-30 03:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0006_auto_20171129_2010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='doctor_name',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='patient_name',
        ),
        migrations.AddField(
            model_name='appointment',
            name='doc',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='website.Doctor'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='website.Profile'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='status',
            field=models.CharField(default=None, max_length=250),
        ),
    ]
