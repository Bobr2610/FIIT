from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Watch, Rate

@shared_task
def notify_currency_rate(watch_id):
    """
    Отправляет уведомление пользователю о текущем курсе валюты.
    """
    try:
        watch = Watch.objects.select_related('portfolio__account', 'currency').get(id=watch_id)
        latest_rate = Rate.objects.filter(currency=watch.currency).latest('timestamp')
        
        message = f"""
        Текущий курс {watch.currency.name} ({watch.currency.short_name}): {latest_rate.cost}
        Время: {latest_rate.timestamp}
        """

        print(message)

        # Отправляем email
        # if watch.portfolio.account.email:
        #     send_mail(
        #         subject=f'Курс {watch.currency.short_name}',
        #         message=message,
        #         from_email=settings.DEFAULT_FROM_EMAIL,
        #         recipient_list=[watch.portfolio.account.email],
        #         fail_silently=True
        #     )
        
        # TODO: Добавить отправку в Telegram, если есть telegram_id
        
    except Watch.DoesNotExist:
        pass  # Запись была удалена
    except Rate.DoesNotExist:
        pass  # Нет курсов для валюты 