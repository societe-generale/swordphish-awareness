# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('Main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='host_subdomain',
            field=models.CharField(blank=True, max_length=200, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[-.a-z0-9]{0,200}(?<!\\.)$', message='Only a-z 0-9 - and ., must not end with a .')]),
        ),
    ]
