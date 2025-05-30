import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FIIT.settings')

app = Celery('FIIT')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    from django_celery_beat.models import CrontabSchedule, PeriodicTask

    schedule, _ = CrontabSchedule.objects.get_or_create(
        hour='*',
        minute='*/5',
        day_of_week='*',
        day_of_month='*',
        month_of_year='*',
    )

    PeriodicTask.objects.create(
        name='update-currency-rates',
        task='app.tasks.update_currency_rates',
        crontab=schedule,
        enabled=True
    )

    PeriodicTask.objects.create(
        name='update-portfolio-values',
        task='api.tasks.update_portfolio_values',
        crontab=schedule,
        enabled=True
    )
