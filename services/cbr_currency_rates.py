import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from requests.exceptions import RequestException
import os
import csv
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CurrencyRate:
    """Класс для хранения информации о курсе валюты."""
    currency: str
    code: str
    nominal: int
    price: float
    date: datetime

class CBRCurrencyRates:
    """Класс для работы с курсами валют Центрального Банка России."""
    
    BASE_URL = "https://www.cbr.ru/scripts/"
    TIMEOUT = 10  # таймаут запроса в секундах
    MAX_RETRIES = 3  # максимальное количество попыток запроса
    
    # Коды валют в API ЦБ РФ
    CURRENCY_CODES = {
        "USD": "R01235",  # Доллар США
        "EUR": "R01239",  # Евро
        "CNY": "R01375",  # Китайский юань
        "AED": "R01230"   # Дирхам ОАЭ
    }
    
    # Названия валют на русском
    CURRENCY_NAMES = {
        "USD": "Доллар США",
        "EUR": "Евро",
        "CNY": "Китайский юань",
        "AED": "Дирхам ОАЭ"
    }
    
    def __init__(self, data_dir: str = None):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        # Директория для сохранения данных
        self.data_dir = data_dir or os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def fetch_currency_rate(self, date: datetime, currency_code: str = "USD") -> Optional[CurrencyRate]:
        """Получение курса валюты на конкретную дату.
        
        Args:
            date (datetime): Дата, на которую нужно получить курс
            currency_code (str, optional): Код валюты (USD, EUR, CNY, AED). По умолчанию USD.
            
        Returns:
            Optional[CurrencyRate]: Информация о курсе валюты или None, если данные недоступны
            
        Raises:
            RequestException: При ошибке запроса к API
            ValueError: Если указан неподдерживаемый код валюты
        """
        if currency_code not in self.CURRENCY_CODES:
            raise ValueError(f"Неподдерживаемый код валюты: {currency_code}. Поддерживаемые коды: {', '.join(self.CURRENCY_CODES.keys())}")
            
        formatted_date = date.strftime('%d/%m/%Y')
        url = f"{self.BASE_URL}XML_daily.asp?date_req={formatted_date}"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=self.TIMEOUT)
                response.raise_for_status()
                return self._parse_daily_xml(response.text, date, currency_code)
            except RequestException as e:
                logger.error(f"Попытка {attempt + 1}/{self.MAX_RETRIES} не удалась: {str(e)}")
                if attempt == self.MAX_RETRIES - 1:
                    raise
                continue
        return None
    
    def fetch_currency_dynamic(self, start_date: datetime, end_date: datetime, currency_code: str = "USD") -> List[CurrencyRate]:
        """Получение динамики курса валюты за период.
        
        Args:
            start_date (datetime): Начальная дата периода
            end_date (datetime): Конечная дата периода
            currency_code (str, optional): Код валюты (USD, EUR, CNY, AED). По умолчанию USD.
            
        Returns:
            List[CurrencyRate]: Список курсов валют за период
            
        Raises:
            RequestException: При ошибке запроса к API
            ValueError: При некорректных данных или неподдерживаемом коде валюты
        """
        if start_date > end_date:
            raise ValueError("Начальная дата должна быть меньше или равна конечной")
            
        if currency_code not in self.CURRENCY_CODES:
            raise ValueError(f"Неподдерживаемый код валюты: {currency_code}. Поддерживаемые коды: {', '.join(self.CURRENCY_CODES.keys())}")
        
        formatted_start = start_date.strftime('%d/%m/%Y')
        formatted_end = end_date.strftime('%d/%m/%Y')
        url = f"{self.BASE_URL}XML_dynamic.asp?date_req1={formatted_start}&date_req2={formatted_end}&VAL_NM_RQ={self.CURRENCY_CODES[currency_code]}"
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(url, timeout=self.TIMEOUT)
                response.raise_for_status()
                return self._parse_dynamic_xml(response.text, currency_code)
            except RequestException as e:
                logger.error(f"Попытка {attempt + 1}/{self.MAX_RETRIES} не удалась: {str(e)}")
                if attempt == self.MAX_RETRIES - 1:
                    raise
                continue
        return []
    
    def fetch_five_year_rates(self, currency_code: str = "USD") -> List[CurrencyRate]:
        """Получение курсов валют за последние пять лет.
        
        Args:
            currency_code (str, optional): Код валюты (USD, EUR, CNY, AED). По умолчанию USD.
            
        Returns:
            List[CurrencyRate]: Список курсов валют за пять лет
            
        Raises:
            RequestException: При ошибке запроса к API
            ValueError: При некорректных данных или неподдерживаемом коде валюты
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 5)  # 5 лет назад
        
        logger.info(f"Получение курсов {currency_code}/RUB за период с {start_date.strftime('%d.%m.%Y')} по {end_date.strftime('%d.%m.%Y')}")
        return self.fetch_currency_dynamic(start_date, end_date, currency_code)
    
    def _parse_daily_xml(self, xml_text: str, date: datetime, currency_code: str = "USD") -> Optional[CurrencyRate]:
        """Парсинг XML-данных о курсах валют на конкретную дату.
        
        Args:
            xml_text (str): XML-данные от API
            date (datetime): Дата курса
            currency_code (str, optional): Код валюты (USD, EUR, CNY, AED). По умолчанию USD.
            
        Returns:
            Optional[CurrencyRate]: Информация о курсе валюты или None, если данные недоступны
        """
        try:
            root = ET.fromstring(xml_text)
            for valute in root.findall('.//Valute'):
                if valute.get('ID') == self.CURRENCY_CODES[currency_code]:
                    code = valute.find('CharCode').text
                    name = valute.find('Name').text
                    nominal = int(valute.find('Nominal').text)
                    value_str = valute.find('Value').text.replace(',', '.')
                    value = float(value_str)
                    
                    return CurrencyRate(
                        currency=name,
                        code=code,
                        nominal=nominal,
                        price=value,
                        date=date
                    )
        except (ET.ParseError, AttributeError, ValueError) as e:
            logger.error(f"Ошибка при парсинге XML: {str(e)}")
        
        return None
    
    def _parse_dynamic_xml(self, xml_text: str, currency_code: str = "USD") -> List[CurrencyRate]:
        """Парсинг XML-данных о динамике курсов валют.
        
        Args:
            xml_text (str): XML-данные от API
            currency_code (str, optional): Код валюты (USD, EUR, CNY, AED). По умолчанию USD.
            
        Returns:
            List[CurrencyRate]: Список курсов валют
        """
        rates = []
        try:
            root = ET.fromstring(xml_text)
            for record in root.findall('.//Record'):
                date_str = record.get('Date')
                date = datetime.strptime(date_str, '%d.%m.%Y')
                
                nominal_element = record.find('Nominal')
                nominal = int(nominal_element.text) if nominal_element is not None else 1
                
                value_element = record.find('Value')
                if value_element is not None:
                    value_str = value_element.text.replace(',', '.')
                    value = float(value_str)
                    
                    rate = CurrencyRate(
                        currency=self.CURRENCY_NAMES[currency_code],
                        code=currency_code,
                        nominal=nominal,
                        price=value,
                        date=date
                    )
                    rates.append(rate)
        except (ET.ParseError, AttributeError, ValueError) as e:
            logger.error(f"Ошибка при парсинге XML: {str(e)}")
        
        return rates
    
    def save_rates_to_json(self, rates: List[CurrencyRate], filename: str = None) -> str:
        """Сохранение курсов валют в JSON-файл.
        
        Args:
            rates (List[CurrencyRate]): Список курсов валют
            filename (str, optional): Имя файла. По умолчанию '{currency_code}_rub_rates_YYYY-MM-DD.json'
        
        Returns:
            str: Путь к сохраненному файлу
        """
        if not rates:
            logger.warning("Нет данных для сохранения")
            return ""
        
        if not filename:
            today = datetime.now().strftime('%Y-%m-%d')
            currency_code = rates[0].code.lower() if rates else "currency"
            filename = f"{currency_code}_rub_rates_{today}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump([{
                    'date': rate.date.strftime('%Y-%m-%d'),
                    'currency': rate.currency,
                    'code': rate.code,
                    'nominal': rate.nominal,
                    'price': rate.price
                } for rate in rates], jsonfile, indent=4, ensure_ascii=False)
            
            logger.info(f"Данные успешно сохранены в JSON файл: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в JSON: {str(e)}")
            return ""

    def save_rates_to_csv(self, rates: List[CurrencyRate], filename: str = None) -> str:
        """Сохранение курсов валют в CSV-файл.
        
        Args:
            rates (List[CurrencyRate]): Список курсов валют
            filename (str, optional): Имя файла. По умолчанию '{currency_code}_rub_rates_YYYY-MM-DD.csv'
            
        Returns:
            str: Путь к сохраненному файлу
        """
        if not rates:
            logger.warning("Нет данных для сохранения")
            return ""
        
        if not filename:
            today = datetime.now().strftime('%Y-%m-%d')
            currency_code = rates[0].code.lower() if rates else "currency"
            filename = f"{currency_code}_rub_rates_{today}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['date', 'currency', 'code', 'nominal', 'price']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for rate in rates:
                    writer.writerow({
                        'date': rate.date.strftime('%Y-%m-%d'),
                        'currency': rate.currency,
                        'code': rate.code,
                        'nominal': rate.nominal,
                        'price': rate.price
                    })
            
            logger.info(f"Данные успешно сохранены в файл: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Ошибка при сохранении данных в CSV: {str(e)}")
            return ""

def main():
    """Пример использования класса CBRCurrencyRates для получения и сохранения курсов валют за 5 лет."""
    cbr_rates = CBRCurrencyRates()
    try:
        # Список поддерживаемых валют
        currencies = ["USD", "EUR", "CNY", "AED"]
        
        for currency in currencies:
            # Получение курсов валюты за последние 5 лет
            rates = cbr_rates.fetch_five_year_rates(currency)
            logger.info(f"Получено {len(rates)} записей о курсах {currency}/RUB")
            
            # Сохранение данных в CSV
            filepath = cbr_rates.save_rates_to_csv(rates)
            if filepath:
                logger.info(f"Данные сохранены в файл: {filepath}")
                
                # Вывод первых 3 записей для примера
                for i, rate in enumerate(rates[:3]):
                    print(f"Дата: {rate.date.strftime('%Y-%m-%d')}, {currency}/RUB: {rate.price:.4f} руб. за {rate.nominal} {rate.code}")
                
                if len(rates) > 3:
                    print(f"... и еще {len(rates) - 3} записей")
                print("\n")
    except Exception as e:
        logger.error(f"Ошибка при получении и сохранении курсов валют: {str(e)}")

if __name__ == "__main__":
    main()