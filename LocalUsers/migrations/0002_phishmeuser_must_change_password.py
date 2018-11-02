# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LocalUsers', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='swordphishuser',
            name='must_change_password',
            field=models.BooleanField(default=False),
        ),
    ]
