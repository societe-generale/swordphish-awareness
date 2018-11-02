# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import ckeditor.fields
import LocalUsers.models
import django.db.models.deletion
import django.core.validators
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('LocalUsers', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnonymousTarget',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uniqueid', models.CharField(default=uuid.uuid4, max_length=36)),
                ('mail_opened', models.BooleanField(default=False)),
                ('link_clicked', models.BooleanField(default=False)),
                ('attachment_opened', models.BooleanField(default=False)),
                ('form_submitted', models.BooleanField(default=False)),
                ('reported', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Attribute',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=240)),
                ('value', models.CharField(max_length=240)),
            ],
        ),
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('campaign_type', models.CharField(default=b'1', max_length=1, choices=[(b'1', 'Simple'), (b'2', 'With Attachment'), (b'3', 'Fake Form')])),
                ('name', models.CharField(max_length=200)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('status', models.CharField(default=b'1', max_length=1, choices=[(b'1', 'Not Started'), (b'2', 'Running'), (b'3', 'Finished')])),
                ('from_name', models.CharField(max_length=50)),
                ('display_name', models.CharField(blank=b'True', max_length=100, null=True, validators=[django.core.validators.RegexValidator(regex=b'^[^@]{1,100}$', message='Display name must not contains @')])),
                ('enable_mail_tracker', models.BooleanField(default=True)),
                ('enable_attachment_tracker', models.BooleanField(default=True)),
                ('testid', models.CharField(default=uuid.uuid4, max_length=36)),
                ('anonymous_targets', models.ManyToManyField(to='Main.AnonymousTarget')),
            ],
        ),
        migrations.CreateModel(
            name='PhishmailDomain',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('domain', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Target',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mail_address', models.EmailField(max_length=254)),
                ('attributes', models.ManyToManyField(to='Main.Attribute')),
            ],
        ),
        migrations.CreateModel(
            name='TargetList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=240)),
                ('creation_date', models.DateTimeField(default=datetime.datetime.now, blank=True)),
                ('author', models.ForeignKey(on_delete=models.SET(LocalUsers.models.get_admin), to='LocalUsers.SwordphishUser', null=True)),
                ('targets', models.ManyToManyField(to='Main.Target')),
            ],
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('template_type', models.CharField(default=1, max_length=1, choices=[(b'#1', 'Mail with link'), (b'1', 'Mail with link template'), (b'#2', 'Mail with attachment'), (b'2', 'Mail with attachment template'), (b'3', 'Attachment template'), (b'#3', 'Action after click'), (b'4', 'Redirection'), (b'5', 'Awareness template'), (b'6', 'Fake form template')])),
                ('name', models.CharField(max_length=200)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=100)),
                ('text', ckeditor.fields.RichTextField()),
                ('author', models.ForeignKey(to='LocalUsers.SwordphishUser', on_delete=models.SET(LocalUsers.models.get_admin))),
            ],
        ),
        migrations.AddField(
            model_name='campaign',
            name='attachment_template',
            field=models.ForeignKey(related_name='campaign_attachment', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='Main.Template', null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='author',
            field=models.ForeignKey(to='LocalUsers.SwordphishUser', on_delete=models.SET(LocalUsers.models.get_admin)),
        ),
        migrations.AddField(
            model_name='campaign',
            name='fake_form',
            field=models.ForeignKey(related_name='campaign_fake_form', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='Main.Template', null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='from_domain',
            field=models.ForeignKey(related_name='campaign_from_domain', on_delete=django.db.models.deletion.PROTECT, to='Main.PhishmailDomain'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='host_domain',
            field=models.ForeignKey(related_name='campaign_host_domain', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='Main.PhishmailDomain', null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='mail_template',
            field=models.ForeignKey(related_name='campaign_mail', on_delete=django.db.models.deletion.PROTECT, to='Main.Template'),
        ),
        migrations.AddField(
            model_name='campaign',
            name='onclick_action',
            field=models.ForeignKey(related_name='campaign_action', on_delete=django.db.models.deletion.PROTECT, default=None, blank=True, to='Main.Template', null=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='targets',
            field=models.ManyToManyField(to='Main.TargetList'),
        ),
        migrations.AddField(
            model_name='anonymoustarget',
            name='attributes',
            field=models.ManyToManyField(to='Main.Attribute'),
        ),
    ]
