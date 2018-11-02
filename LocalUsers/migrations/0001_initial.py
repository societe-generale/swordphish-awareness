# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='SwordphishUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone_number', models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator(regex=b'^\\+?1?\\d{9,15}$', message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")])),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('entity', models.ForeignKey(to='LocalUsers.Entity', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='RegionMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('region', models.ForeignKey(to='LocalUsers.Region', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to='LocalUsers.SwordphishUser', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='region',
            name='members',
            field=models.ManyToManyField(to='LocalUsers.SwordphishUser', through='LocalUsers.RegionMembership'),
        ),
        migrations.AddField(
            model_name='entity',
            name='admins',
            field=models.ManyToManyField(to='LocalUsers.SwordphishUser'),
        ),
    ]
