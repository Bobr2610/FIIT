import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FIIT.settings')

app = Celery('FIIT')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.conf.beat_schedule['update-currency-rates'] = {
        'task': 'app.tasks.update_currency_rates',
        'schedule': crontab(minute='*/5'),
    }
