# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-06-01 18:28
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='course',
            name='knowledge_area',
        ),
    ]
