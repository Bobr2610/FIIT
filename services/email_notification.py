import os
import sys
import django
from django.core.mail import send_mail
from django.conf import settings

# Настраиваем Django
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'FIIT.settings')
django.setup()

class EmailNotificationService:
    @staticmethod
    def send_rate_notification(email: str, currency_name: str, rate: float, timestamp: str) -> bool:
        """Отправка уведомления о курсе валюты."""
        try:
            subject = f'Обновление курса {currency_name}'
            message = (
                f'Уважаемый пользователь!\n\n'
                f'Курс {currency_name} обновился:\n'
                f'Текущий курс: {rate}\n'
                f'Время обновления: {timestamp}\n\n'
                f'С уважением,\nКоманда FIIT'
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            return True
        except Exception as e:
            print(f'Ошибка отправки email: {str(e)}')
            return False
    
    @staticmethod
    def send_portfolio_notification(email: str, portfolio_value: float, change_percent: float) -> bool:
        """Отправка уведомления об изменении стоимости портфеля."""
        try:
            subject = 'Изменение стоимости портфеля'
            message = (
                f'Уважаемый пользователь!\n\n'
                f'Произошло значительное изменение стоимости вашего портфеля:\n'
                f'Текущая стоимость: {portfolio_value:.2f}\n'
                f'Изменение: {change_percent:+.2f}%\n\n'
                f'С уважением,\nКоманда FIIT'
            )
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False
            )
            return True
        except Exception as e:
            print(f'Ошибка отправки email: {str(e)}')
            return False

# Пример использования:
if __name__ == '__main__':
    # Тестовая отправка
    service = EmailNotificationService()
'''    service.send_rate_notification(
        email='test@example.com',
        currency_name='USD',
        rate=75.5,
        timestamp='2024-01-01 12:00:00'
    )'''