import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FIIT.settings')

app = Celery('FIIT')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(300.0, update_currencies.s(), name='update currencies')


@app.task
def update_currencies():
    print('TODO: !!!Hello!!!')
