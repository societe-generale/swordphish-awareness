from __future__ import absolute_import, unicode_literals
from celery import Celery
from django.conf import settings


# set the default Django settings module for the 'celery' program.
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Swordphish.settings')

app = Celery(
    'Swordphish',
    broker='redis://%s:%d/%d' % (settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB),
    backend='redis://%s:%d/%d' % (settings.REDIS_HOST, settings.REDIS_PORT, settings.REDIS_DB)
)

app.autodiscover_tasks()

app.conf.timezone = "Europe/Paris"
