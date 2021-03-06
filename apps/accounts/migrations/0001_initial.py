# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-25 19:55
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import miprepa.utils.mixins


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('universities', '0001_initial'),
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(max_length=150, unique=True)),
                ('nickname', models.CharField(max_length=100, unique=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('photo', models.ImageField(null=True, upload_to='users/photos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('gender', models.CharField(blank=True, choices=[('m', 'Masculino'), ('f', 'Femenino')], max_length=1)),
                ('birthday', models.DateField(blank=True, null=True)),
                ('is_new', models.BooleanField(default=True)),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Usuario',
                'verbose_name_plural': 'Usuarios',
            },
            bases=(miprepa.utils.mixins.UidMixin, models.Model),
        ),
        migrations.CreateModel(
            name='UserUniversity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('experience', models.IntegerField(default=0, verbose_name='Experiencia')),
                ('follows', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), blank=True, null=True, size=None, verbose_name='Seguidos')),
                ('first_option', models.BooleanField(default=False)),
                ('desired_university', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_universities', to='universities.University')),
                ('knowledge_area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_universities', to='universities.KnowledgeArea')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_universities', to=settings.AUTH_USER_MODEL)),
            ],
            bases=(miprepa.utils.mixins.UidMixin, models.Model),
        ),
        migrations.AddField(
            model_name='user',
            name='desired_university',
            field=models.ManyToManyField(related_name='candidates', through='accounts.UserUniversity', to='universities.University'),
        ),
        migrations.AddField(
            model_name='user',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AddField(
            model_name='user',
            name='user_permissions',
            field=models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions'),
        ),
        migrations.AlterUniqueTogether(
            name='useruniversity',
            unique_together=set([('user', 'desired_university')]),
        ),
    ]
