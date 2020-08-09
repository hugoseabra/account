import os

from celery import Celery
from kombu import Queue, Exchange

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('account-service')
app.config_from_object('django.conf:settings', namespace='CELERY')

app_names = (
    'avatar',
)

queues = list()

for app_name in app_names:
    queues.append(Queue(
        name=app_name,
        exchange=Exchange(name='account-service',
                          type='direct',
                          delivery_mode=2),
        routing_key=app_name,
        durable=True,
    ))

app.conf.task_queues = queues

app.autodiscover_tasks()
