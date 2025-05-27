from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import Watch, Rate, Portfolio, CurrencyBalance
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

@shared_task
def update_portfolio_values():
    portfolios = Portfolio.objects.all()
    
    for portfolio in portfolios:
        total_value = portfolio.balance
        
        currency_balances = CurrencyBalance.objects.filter(portfolio=portfolio).select_related('currency')
        
        for balance in currency_balances:
            try:
                current_rate = balance.currency.rate_set.latest('timestamp')
                total_value += balance.amount * current_rate.cost
            except Rate.DoesNotExist:
                continue
        
        cache_key = f'portfolio_value_{portfolio.id}'
        previous_value = cache.get(cache_key)
        
        if previous_value is not None:
            change_percent = ((total_value - previous_value) / previous_value) * 100
            
            if portfolio.notify_threshold is not None and abs(change_percent) >= portfolio.notify_threshold:
                message = (
                    f"<b>Изменение стоимости портфеля</b>\n\n"
                    f"💰 Текущая стоимость: {total_value}\n"
                    f"📈 Изменение: {'+' if change_percent > 0 else ''}{change_percent:.2f}%\n"
                    f"⏰ Время: {timezone.now().strftime('%H:%M:%S')}"
                )
                
                if portfolio.account.telegram_chat_id:
                    try:
                        asyncio.run(send_telegram_notification(
                            chat_id=portfolio.account.telegram_chat_id,
                            message=message
                        ))
                    except Exception:
                        pass

                if portfolio.account.email:
                    try:
                        send_mail(
                            subject=f'Изменение стоимости портфеля',
                            message=message,
                            from_email=settings.DEFAULT_FROM_EMAIL,
                            recipient_list=[portfolio.account.email],
                            fail_silently=True
                        )
                    except Exception:
                        pass
        
        cache.set(cache_key, total_value, timeout=3600)
