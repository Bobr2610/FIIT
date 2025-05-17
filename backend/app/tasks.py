from celery import shared_task


@shared_task
def update_currency_rates():
    print('TODO: !!!Hello!!!')
