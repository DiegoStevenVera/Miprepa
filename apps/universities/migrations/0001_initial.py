# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-25 19:55
from __future__ import unicode_literals

from django.db import migrations, models
import miprepa.utils.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KnowledgeArea',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('image', models.ImageField(blank=True, null=True, upload_to='universities/images/')),
                ('is_enabled', models.BooleanField(default=True)),
            ],
            bases=(miprepa.utils.mixins.UidMixin, models.Model),
        ),
        migrations.CreateModel(
            name='University',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=200)),
                ('image', models.ImageField(upload_to='universities/images/')),
                ('is_enabled', models.BooleanField(default=True)),
            ],
            bases=(miprepa.utils.mixins.UidMixin, models.Model),
        ),
    ]
