from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Watch, Rate
import asyncio
import aiohttp

async def send_telegram_notification(chat_id: int, message: str) -> bool:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": chat_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
            ) as response:
                return response.status == 200
    except Exception:
        return False

@shared_task
def notify_currency_rate(watch_id):
    try:
        watch = Watch.objects.select_related('portfolio__account', 'currency').get(id=watch_id)
        latest_rate = Rate.objects.filter(currency=watch.currency).latest('timestamp')
        
        message = (
            f"<b>Обновление курса валют</b>\n\n"
            f"💱 {watch.currency.name} ({watch.currency.short_name})\n"
            f"📈 Курс: {latest_rate.cost}\n"
            f"⏰ Время: {latest_rate.timestamp}"
        )

        if watch.portfolio.account.telegram_chat_id:
            try:
                asyncio.run(send_telegram_notification(
                    chat_id=watch.portfolio.account.telegram_chat_id,
                    message=message
                ))
            except Exception:
                pass

        # TODO: исправить почту
        if watch.portfolio.account.email:
            try:
                send_mail(
                    subject=f'Курс {watch.currency.short_name}',
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[watch.portfolio.account.email],
                    fail_silently=True
                )
            except Exception:
                pass
        
    except (Watch.DoesNotExist, Rate.DoesNotExist):
        pass 