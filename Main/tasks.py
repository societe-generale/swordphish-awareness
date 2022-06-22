# coding: utf8


from __future__ import absolute_import, unicode_literals
from datetime import timedelta
from celery.schedules import crontab
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import EmailMessage

from Swordphish.celery import app as celery_app

from Main.models import Campaign, Attribute, TargetList, AnonymousTarget, Target


celery_app.conf.beat_schedule['update-every-minute'] = {
    'task': 'Main.tasks.check_campaigns',
    'schedule': crontab(),
    'args': (),
}

celery_app.conf.beat_schedule['run-every-saturday-night'] = {
    'task': 'Main.tasks.clean_database',
    'schedule': crontab(hour=22, minute=00, day_of_week=settings.AUTOCLEAN_DAY)
}

celery_app.conf.beat_schedule['run-every-day'] = {
    'task': 'Main.tasks.auto_lock_users',
    'schedule': crontab(hour=12, minute=00)
}


@celery_app.task
def check_campaigns():
    now = timezone.now()

    campaigns = Campaign.objects.filter(status="1")
    campaigns_to_start = []
    for campaign in campaigns:
        if campaign.start_date <= now:
            if campaign.end_date >= now:
                campaign.status = "2"
                campaign.save()
                campaigns_to_start.append(campaign)

    for campaign in campaigns_to_start:
        start_campaign.delay(campaign.id)

    campaigns = Campaign.objects.filter(status="2")
    for campaign in campaigns:
        if campaign.end_date <= now:
            campaign.stop()
            campaign.generate_results_xlsx()


@celery_app.task
def start_campaign(campaign_id):
    campaign = Campaign.objects.get(pk=campaign_id)
    campaign.start()


@celery_app.task
def clean_database():
    time_delta = timezone.now() - timedelta(days=settings.AUTOCLEAN_DELAY)

    campaigns_to_delete = Campaign.objects.filter(creation_date__lt=time_delta, status=3)
    for c in campaigns_to_delete:
        c.delete()

    targetlist_to_delete = TargetList.objects.filter(creation_date__lt=time_delta, campaign=None)
    for t in targetlist_to_delete:
        t.delete()

    targets_to_delete = Target.objects.filter(targetlist=None)
    for t in targets_to_delete:
        t.delete()

    anonymoustarget_to_delete = AnonymousTarget.objects.filter(campaign=None)
    for a in anonymoustarget_to_delete:
        a.delete()

    attributes_to_delete = Attribute.objects.filter(target=None, anonymoustarget=None)
    for a in attributes_to_delete:
        a.delete()


@celery_app.task
def auto_lock_users():
    template_never_used = settings.AUTOLOCK_TEMPLATE

    template_used_since = settings.AUTOLOCK_NEVER_USED_TEMPLATE

    time_delta = timezone.now() - timedelta(days=settings.AUTOLOCK_NEVER_USED_DELAY)
    users = User.objects.filter(swordphishuser__must_change_password=True,
                                is_active=True,
                                last_login=None,
                                date_joined__lt=time_delta
                                )
    for u in users:
        u.is_active = False
        u.save()
        message = EmailMessage(from_email=settings.USER_ACCOUNT_CREATION_MAIL_SENDER,
                               subject=settings.USER_ACCOUNT_LOCKED_MAIL_TITLE,
                               body=template_never_used % (u.first_name),
                               to=[u.email],
                               cc=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT],
                               reply_to=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT]
                               )
        message.send()

    time_delta = timezone.now() - timedelta(days=settings.AUTOLOCK_DELAY)
    users = User.objects.filter(last_login__lt=time_delta, is_active=True)
    for u in users:
        u.is_active = False
        u.save()
        message = EmailMessage(from_email=settings.USER_ACCOUNT_CREATION_MAIL_SENDER,
                               subject=settings.USER_ACCOUNT_LOCKED_MAIL_TITLE,
                               body=template_used_since % (u.first_name, settings.AUTOLOCK_DELAY),
                               to=[u.email],
                               cc=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT],
                               reply_to=[settings.USER_ACCOUNT_CREATION_MAIL_CONTACT]
                               )
        message.send()
