import requests
from datetime import datetime
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from requests.exceptions import RequestException

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CurrencyRate:
    """Класс для хранения информации о курсе валюты."""
    currency: str
    price: float
    datetime: datetime

class MoexCurrencyRates:
    """Класс для работы с курсами валют Московской биржи."""
    
    BASE_URL = "https://www.moex.com/api/"
    TIMEOUT = 10  # таймаут запроса в секундах
    MAX_RETRIES = 3  # максимальное количество попыток запроса

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_currency_rates(self) -> List[CurrencyRate]:
        """
        Получение курсов валют с Московской биржи.
        
        Returns:
            List[CurrencyRate]: Список курсов валют
            
        Raises:
            RequestException: При ошибке запроса к API
            ValueError: При некорректных данных
        """
        url = f"{self.BASE_URL}currency_rates"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=self.TIMEOUT)
                response.raise_for_status()
                return self.parse_currency_rates(response.json())
            except RequestException as e:
                logger.error(f"Попытка {attempt + 1}/{self.MAX_RETRIES} не удалась: {str(e)}")
                if attempt == self.MAX_RETRIES - 1:
                    raise
                continue

    def parse_currency_rates(self, data: Dict[str, Any]) -> List[CurrencyRate]:
        """
        Парсинг данных о курсах валют.
        
        Args:
            data (Dict[str, Any]): JSON-данные от API
            
        Returns:
            List[CurrencyRate]: Список курсов валют
            
        Raises:
            ValueError: При некорректном формате данных
        """
        if not isinstance(data, dict) or 'rates' not in data:
            raise ValueError("Некорректный формат данных от API")

        rates = []
        for item in data['rates']:
            try:
                rate = CurrencyRate(
                    currency=item['currency'],
                    price=float(item['price']),
                    datetime=datetime.strptime(item['datetime'], '%Y-%m-%dT%H:%M:%S')
                )
                rates.append(rate)
            except (KeyError, ValueError) as e:
                logger.warning(f"Пропущена некорректная запись: {str(e)}")
                continue
                
        return rates

def main():
    """Пример использования класса MoexCurrencyRates."""
    moex_rates = MoexCurrencyRates()
    try:
        rates = moex_rates.fetch_currency_rates()
        for rate in rates:
            print(f"Валюта: {rate.currency}, Цена: {rate.price:.4f}, "
                  f"Дата/время: {rate.datetime.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logger.error(f"Ошибка при получении курсов валют: {str(e)}")

if __name__ == "__main__":
    main()