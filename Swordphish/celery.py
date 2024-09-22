from celery import Celery

app = Celery(
    'Swordphish',
    broker='sqla+sqlite:///celery_broker.sqlite',
    backend='db+sqlite:///celery_backend.sqlite'
)

app.autodiscover_tasks()
app.conf.timezone = "Europe/Paris"
