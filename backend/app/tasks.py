from celery import shared_task
from datetime import datetime, timedelta, timezone
import requests
import xml.etree.ElementTree as ET
from api.models import Currency, Rate
from django.db import transaction
from typing import List, Dict, Any
from dataclasses import dataclass
from django.utils import timezone as django_timezone

@dataclass
class CurrencyRate:
    currency: str
    code: str
    price: float
    date: datetime

class CurrencyRatesService:

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
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def __del__(self):
        if hasattr(self, 'session'):
            self.session.close()
    
    def get_rates(self, start_date: datetime, end_date: datetime) -> Dict[str, List[CurrencyRate]]:
        try:
            rates = {}
            
            # Получаем курсы фиатных валют от ЦБ РФ
            for currency_code in self.CBR_CODES:
                rates[currency_code] = self._get_cbr_rates(currency_code, start_date, end_date)
            
            # Получаем курс USDT/RUB
            usdt_rub_rates = self._get_usdt_rub_rates(start_date, end_date)
            
            # Получаем курсы криптовалют от Binance
            for symbol in self.BINANCE_PAIRS:
                klines = self._get_binance_rates(symbol, start_date, end_date)
                if klines and usdt_rub_rates:
                    rates[symbol] = self._convert_crypto_rates(symbol, klines, usdt_rub_rates)
            
            return rates
        except Exception as e:
            print(f"Ошибка при получении курсов: {e}")
            return {}
    
    def _get_cbr_rates(self, currency_code: str, start_date: datetime, end_date: datetime) -> List[CurrencyRate]:
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
    
    def _get_usdt_rub_rates(self, start_date: datetime, end_date: datetime) -> Dict[str, float]:
        try:
            params = {
                'symbol': 'USDTRUB',
                'interval': '1d',
                'startTime': int(start_date.timestamp() * 1000),
                'endTime': int(end_date.timestamp() * 1000),
                'limit': 1000
            }
            
            response = self.session.get("https://api.binance.com/api/v3/klines", params=params, timeout=10)
            response.raise_for_status()
            klines = response.json()
            
            rates = {}
            for k in klines:
                date = django_timezone.localtime(datetime.fromtimestamp(k[0] // 1000, tz=timezone.utc))
                close = float(k[4])
                rates[date.strftime('%Y-%m-%d')] = close
            
            return rates
        except Exception as e:
            print(f"Ошибка при получении курса USDT/RUB: {e}")
            return {}
    
    def _convert_crypto_rates(self, symbol: str, klines: List[Dict[str, Any]], usdt_rub_rates: Dict[str, float]) -> List[CurrencyRate]:
        try:
            rates = []
            for k in klines:
                date = django_timezone.localtime(datetime.fromtimestamp(k[0] // 1000, tz=timezone.utc))
                close_usdt = float(k[4])
                rub = usdt_rub_rates.get(date.strftime('%Y-%m-%d'))
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
    try:
        service = CurrencyRatesService()
        end_date = django_timezone.now()
        start_date = end_date - timedelta(days=365)

        rates = service.get_rates(start_date, end_date)

        with transaction.atomic():
            for currency_code, currency_rates in rates.items():
                currency = Currency.objects.get(short_name=currency_code)
                for rate in currency_rates:
                    Rate.objects.create(
                        currency=currency,
                        cost=rate.price,
                        timestamp=rate.date
                    )

        return True
    except Exception as e:
        print(f"Ошибка при обновлении курсов валют: {e}")
        return False
    finally:
        if 'service' in locals():
            del service
