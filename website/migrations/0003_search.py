# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-29 01:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20171128_1630'),
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search', models.CharField(default=None, max_length=250)),
                ('attribute', models.CharField(default=None, max_length=250)),
            ],
        ),
    ]
