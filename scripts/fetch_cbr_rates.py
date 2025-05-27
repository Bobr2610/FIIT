#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Скрипт для получения и сохранения исторических данных о курсах валют (USD, EUR, CNY, AED)
к рублю (RUB) за последние пять лет с использованием API Центрального Банка России.
"""

import sys
import os
import logging
from datetime import datetime

# Добавляем родительскую директорию в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.cbr_currency_rates import CBRCurrencyRates

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Основная функция для получения и сохранения курсов валют к рублю."""
    logger.info("Запуск скрипта получения исторических данных о курсах валют к рублю")
    
    # Создаем экземпляр класса для работы с API ЦБР
    cbr_rates = CBRCurrencyRates()
    
    # Список поддерживаемых валют
    currencies = ["USD", "EUR", "CNY", "AED"]
    
    try:
        for currency in currencies:
            # Получаем курсы валюты за последние 5 лет
            logger.info(f"Получение курсов {currency}/RUB за последние 5 лет...")
            rates = cbr_rates.fetch_five_year_rates(currency)
            
            if not rates:
                logger.error(f"Не удалось получить данные о курсах {currency}/RUB")
                continue
            
            logger.info(f"Успешно получено {len(rates)} записей для {currency}/RUB")
            
            # Формируем имя файла с текущей датой
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f"{currency.lower()}_rub_5year_rates_{today}.csv"
            
            # Сохраняем данные в CSV-файл
            logger.info(f"Сохранение данных в файл {filename}...")
            # Save to both CSV and JSON
            csv_filepath = cbr_rates.save_rates_to_csv(rates, filename)
            json_filename = filename.replace('.csv', '.json')
            json_filepath = cbr_rates.save_rates_to_json(rates, json_filename)
            filepath = json_filepath
            
            if not filepath:
                logger.error(f"Не удалось сохранить данные {currency}/RUB в файл")
                continue
            
            logger.info(f"Данные {currency}/RUB успешно сохранены в файл: {filepath}")
            
            # Выводим статистику
            if rates:
                earliest_date = min(rate.date for rate in rates)
                latest_date = max(rate.date for rate in rates)
                min_rate = min(rates, key=lambda x: x.price)
                max_rate = max(rates, key=lambda x: x.price)
                
                print(f"\nСтатистика по курсам {currency}/RUB:")
                print(f"Период: с {earliest_date.strftime('%d.%m.%Y')} по {latest_date.strftime('%d.%m.%Y')}")
                print(f"Всего записей: {len(rates)}")
                print(f"Минимальный курс: {min_rate.price:.4f} руб. ({min_rate.date.strftime('%d.%m.%Y')})")
                print(f"Максимальный курс: {max_rate.price:.4f} руб. ({max_rate.date.strftime('%d.%m.%Y')})")
                print(f"Данные сохранены в: {filepath}")
                print("-----------------------------------")
        
        return 0
    except Exception as e:
        logger.error(f"Произошла ошибка при выполнении скрипта: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())