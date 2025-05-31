from celery import shared_task
from datetime import datetime, timedelta, timezone
import requests
import xml.etree.ElementTree as ET
from api.models import Currency, Rate
from django.db import transaction
from typing import List, Dict, Any
from dataclasses import dataclass
from django.utils import timezone as django_timezone
from django.core.cache import cache

@dataclass
class CurrencyRate:
    """
    Представляет курс валюты с сопутствующими метаданными.

    Атрибуты:
        currency (str): Название валюты.
        code (str): Краткий код валюты.
        price (float): Курс обмена.
        date (datetime): Дата курса обмена.
    """
    currency: str
    code: str
    price: float
    date: datetime

class CurrencyRatesService:
    """
    Сервис для получения и обработки курсов валют из внешних API.

    Атрибуты:
        CBR_CODES (dict): Сопоставление кодов валют с их идентификаторами для ЦБ РФ.
        BINANCE_PAIRS (dict): Сопоставление символов криптовалют с их торговыми парами Binance.
    """

    CBR_CODES = {
        "USD": "R01235",
        "EUR": "R01239",
        "CNY": "R01375",
        "AED": "R01230"
    }

    BINANCE_PAIRS = {
        'BTC': 'BTCUSDT',
        'ETH': 'ETHUSDT'
    }

    def __init__(self):
        """
        Инициализирует CurrencyRatesService с сессией запросов.
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def __del__(self):
        """
        Закрывает сессию запросов при удалении сервиса.
        """
        if hasattr(self, 'session'):
            self.session.close()

    def get_rates(self, start_date: datetime, end_date: datetime) -> Dict[str, List[CurrencyRate]]:
        """
        Получает курсы валют от ЦБ РФ и Binance.

        Аргументы:
            start_date (datetime): Начальная дата для получения курсов.
            end_date (datetime): Конечная дата для получения курсов.

        Возвращает:
            dict: Словарь, содержащий списки объектов CurrencyRate для каждой валюты.
        """
        try:
            rates = {}

            # Получение курсов фиатных валют от ЦБ РФ
            for currency_code in self.CBR_CODES:
                rates[currency_code] = self._get_cbr_rates(currency_code, start_date, end_date)

            # Получение курсов криптовалют от Binance и конвертация через USD/RUB
            usd_rates = rates.get('USD', [])
            if usd_rates:
                usd_rub_rates = {rate.date.strftime('%Y-%m-%d'): rate.price for rate in usd_rates}
                for symbol in self.BINANCE_PAIRS:
                    klines = self._get_binance_rates(symbol, start_date, end_date)
                    if klines and usd_rub_rates:
                        rates[symbol] = self._convert_crypto_rates(symbol, klines, usd_rub_rates)

            return rates
        except Exception as e:
            print(f"Ошибка при получении курсов: {e}")
            return {}

    def _get_cbr_rates(self, currency_code: str, start_date: datetime, end_date: datetime) -> List[CurrencyRate]:
        """
        Получает курсы валют от ЦБ РФ.

        Аргументы:
            currency_code (str): Код валюты для получения курсов.
            start_date (datetime): Начальная дата для получения курсов.
            end_date (datetime): Конечная дата для получения курсов.

        Возвращает:
            list: Список объектов CurrencyRate.
        """
        try:
            formatted_start = start_date.strftime('%d/%m/%Y')
            formatted_end = end_date.strftime('%d/%m/%Y')
            url = f"https://www.cbr.ru/scripts/XML_dynamic.asp?date_req1={formatted_start}&date_req2={formatted_end}&VAL_NM_RQ={self.CBR_CODES[currency_code]}"

            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            root = ET.fromstring(response.text)
            rates = []

            for record in root.findall('.//Record'):
                date_str = record.get('Date')
                date = django_timezone.make_aware(datetime.strptime(date_str, '%d.%m.%Y'))
                value_str = record.find('Value').text.replace(',', '.')
                value = float(value_str)

                rate = CurrencyRate(
                    currency=currency_code,
                    code=currency_code,
                    price=value,
                    date=date
                )
                rates.append(rate)

            return rates
        except Exception as e:
            print(f"Ошибка при получении курсов ЦБ РФ для {currency_code}: {e}")
            return []

    def _get_binance_rates(self, symbol: str, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Получает курсы криптовалют от Binance.

        Аргументы:
            symbol (str): Символ криптовалюты для получения курсов.
            start_date (datetime): Начальная дата для получения курсов.
            end_date (datetime): Конечная дата для получения курсов.

        Возвращает:
            list: Список словарей с данными курсов Binance.
        """
        try:
            params = {
                'symbol': self.BINANCE_PAIRS[symbol],
                'interval': '1d',
                'startTime': int(start_date.timestamp() * 1000),
                'endTime': int(end_date.timestamp() * 1000),
                'limit': 1000
            }

            response = self.session.get("https://api.binance.com/api/v3/klines", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка при получении курсов Binance для {symbol}: {e}")
            return []

    def _convert_crypto_rates(self, symbol: str, klines: List[Dict[str, Any]], usd_rub_rates: Dict[str, float]) -> List[CurrencyRate]:
        """
        Конвертирует курсы криптовалют от Binance в рубли с использованием курсов USD/RUB.

        Аргументы:
            symbol (str): Символ криптовалюты.
            klines (list): Список данных курсов Binance.
            usd_rub_rates (dict): Словарь курсов USD/RUB.

        Возвращает:
            list: Список объектов CurrencyRate.
        """
        try:
            rates = []
            for k in klines:
                date = django_timezone.localtime(datetime.fromtimestamp(k[0] // 1000, tz=timezone.utc))
                close_usdt = float(k[4])
                rub = usd_rub_rates.get(date.strftime('%Y-%m-%d'))
                if rub is not None:
                    price_rub = close_usdt * rub
                    rate = CurrencyRate(
                        currency=symbol,
                        code=symbol,
                        price=round(price_rub, 4),
                        date=date
                    )
                    rates.append(rate)
            return rates
        except Exception as e:
            print(f"Ошибка при конвертации курсов для {symbol}: {e}")
            return []

@shared_task
def update_currency_rates():
    """
    Обновляет курсы валют, получая данные из внешних API и сохраняя новые курсы в базе данных.

    Возвращает:
        bool: True, если обновление прошло успешно, False в противном случае.
    """
    try:
        service = CurrencyRatesService()
        end_date = django_timezone.now()

        # Получение последнего временного штампа для каждой валюты        # Проверяем наличие данных в кэше
        latest_rates = cache.get('latest_rates')
        if not latest_rates:
            # Инициализируем пустой словарь для хранения временных штампов
            latest_rates = {}
            for code in list(CurrencyRatesService.CBR_CODES.keys()) + list(CurrencyRatesService.BINANCE_PAIRS.keys()):
                # Фильтруем записи по краткому названию валюты
                latest_rate = Rate.objects.filter(
                    currency__short_name=code
                # Получаем последнюю запись по временной метке
                ).order_by('-timestamp').first()
                # Сохраняем временную метку или None, если записи нет
                latest_rates[code] = latest_rate.timestamp if latest_rate else None
            # Сохраняем данные в кэш с таймаутом 3600 секунд
            cache.set('latest_rates', latest_rates, timeout=3600)

        # Установка начальной даты на основе последних данных или по умолчанию на 365 дней
        start_date = end_date - timedelta(days=365)
        rates = service.get_rates(start_date, end_date)

        with transaction.atomic():
            for currency_code, currency_rates in rates.items():
                currency = Currency.objects.select_related().get(short_name=currency_code)
                latest_timestamp = latest_rates.get(currency_code)

                # Фильтрация новых данных
                new_rates = [rate for rate in currency_rates if not latest_timestamp or rate.date > latest_timestamp]

                # Пакетная вставка новых курсов
                Rate.objects.bulk_create([
                    Rate(
                        currency=currency,
                        cost=rate.price,
                        timestamp=rate.date
                    ) for rate in new_rates
                ])

        return True
    except Exception as e:
        print(f"Ошибка при обновлении курсов валют: {e}")
        return False
    finally:
        if 'service' in locals():
            del service
