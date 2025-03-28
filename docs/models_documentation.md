# Документация моделей Django

## Модель Currency

Модель `Currency` представляет собой валюту и содержит следующие поля:

- `name`: Полное название валюты. Тип данных - `CharField` с максимальной длиной 64 символа.
- `short_name`: Краткое название валюты (например, USD, EUR). Тип данных - `CharField` с максимальной длиной 3 символа.

Метод `__str__` возвращает краткое название валюты.

## Модель Rate

Модель `Rate` представляет собой курс валюты и содержит следующие поля:

- `currency`: Ссылка на модель `Currency`, представляющая валюту, к которой относится курс. Используется `ForeignKey` с каскадным удалением.
- `price`: Цена валюты. Тип данных - `FloatField`.
- `datetime`: Дата и время, когда был установлен курс. Тип данных - `DateTimeField`.

Метод `__str__` возвращает полное название валюты, к которой относится курс.

# Документация моделей Django

## Модель Currency

Модель `Currency` представляет собой валюту и содержит следующие поля:

- `name`: Полное название валюты. Тип данных - `CharField` с максимальной длиной 64 символа.
- `short_name`: Краткое название валюты (например, USD, EUR). Тип данных - `CharField` с максимальной длиной 3 символа.

Метод `__str__` возвращает краткое название валюты.

## Модель Rate

Модель `Rate` представляет собой курс валюты и содержит следующие поля:

- `currency`: Ссылка на модель `Currency`, представляющая валюту, к которой относится курс. Используется `ForeignKey` с каскадным удалением.
- `price`: Цена валюты. Тип данных - `FloatField`.
- `datetime`: Дата и время, когда был установлен курс. Тип данных - `DateTimeField`.

Метод `__str__` возвращает полное название валюты, к которой относится курс.

## Класс MoexCurrencyRates

Класс `MoexCurrencyRates` используется для получения и обработки курсов валют с Московской биржи (MOEX).

### Методы

- `fetch_currency_rates()`: Получает курсы валют с MOEX. Возвращает список курсов, если запрос успешен, или вызывает исключение в случае ошибки.

- `parse_currency_rates(data)`: Обрабатывает данные курсов валют, полученные с MOEX. Преобразует данные в список словарей, содержащих информацию о валюте, цене и дате/времени.

### Пример использования

```python
moex_rates = MoexCurrencyRates()
try:
    rates = moex_rates.fetch_currency_rates()
    for rate in rates:
        print(f"Currency: {rate['currency']}, Price: {rate['price']}, DateTime: {rate['datetime']}")
except Exception as e:
    print(e)
```

Этот класс позволяет интегрировать курсы валют MOEX в ваше приложение, предоставляя актуальные данные о валютных курсах.