from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account, Portfolio, Operation, Currency, CurrencyHistory, Rate

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели пользователя Django (User).

    Преобразует данные пользователя между форматами Python и JSON для API.
    
    Атрибуты:
        model (User): Модель пользователя Django
        fields (tuple): Поля модели для сериализации
        read_only_fields (tuple): Поля, доступные только для чтения
    
    Поля:
        id (int): Уникальный идентификатор пользователя (только для чтения)
        username (str): Имя пользователя (обязательное поле)
        email (str): Электронная почта пользователя (обязательное поле)
    
    Пример использования:
        # Создание нового пользователя
        serializer = UserSerializer(data={'username': 'user1', 'email': 'user1@example.com'})
        if serializer.is_valid():
            user = serializer.save()
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)

class AccountSerializer(serializers.ModelSerializer):
    """Сериализатор для модели аккаунта пользователя (Account).

    Расширяет базовую информацию о пользователе, добавляя поле для Telegram.
    
    Атрибуты:
        model (Account): Модель аккаунта
        fields (tuple): Поля модели для сериализации
        read_only_fields (tuple): Поля, доступные только для чтения
    
    Поля:
        id (int): Уникальный идентификатор аккаунта (только для чтения)
        username (str): Имя пользователя (обязательное поле)
        email (str): Электронная почта пользователя (обязательное поле)
        telegram (str): Ссылка на Telegram пользователя (необязательное поле)
    
    Пример использования:
        # Обновление данных аккаунта
        serializer = AccountSerializer(account, data={'telegram': '@username'})
        if serializer.is_valid():
            updated_account = serializer.save()
    """
    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'telegram')
        read_only_fields = ('id',)

class PortfolioSerializer(serializers.ModelSerializer):
    """Сериализатор для модели портфеля пользователя (Portfolio).

    Обрабатывает данные инвестиционного портфеля, связанного с аккаунтом пользователя.
    
    Атрибуты:
        model (Portfolio): Модель портфеля
        fields (tuple): Поля модели для сериализации
        read_only_fields (tuple): Поля, доступные только для чтения
    
    Поля:
        id (int): Уникальный идентификатор портфеля (только для чтения)
        account (int): ID аккаунта владельца портфеля (внешний ключ)
    
    Пример использования:
        # Создание нового портфеля
        serializer = PortfolioSerializer(data={'account': account_id})
        if serializer.is_valid():
            portfolio = serializer.save()
    """
    class Meta:
        model = Portfolio
        fields = ('id', 'account')
        read_only_fields = ('id',)

class OperationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели операций в портфеле (Operation).

    Обрабатывает данные операций покупки/продажи финансовых инструментов.
    
    Атрибуты:
        model (Operation): Модель операции
        fields (tuple): Поля модели для сериализации
        read_only_fields (tuple): Поля, доступные только для чтения
    
    Поля:
        id (int): Уникальный идентификатор операции (только для чтения)
        portfolio (int): ID портфеля, в котором совершена операция (внешний ключ)
        operation_type (str): Тип операции ('BUY' или 'SELL')
        product (str): Название финансового инструмента
        amount (int): Количество купленных/проданных единиц
        price (decimal): Цена за единицу
        timestamp (datetime): Время совершения операции (автоматически)
    
    Пример использования:
        # Регистрация новой операции покупки
        data = {
            'portfolio': portfolio_id,
            'operation_type': 'BUY',
            'product': 'USD',
            'amount': 100,
            'price': 75.50
        }
        serializer = OperationSerializer(data=data)
        if serializer.is_valid():
            operation = serializer.save()
    """
    class Meta:
        model = Operation
        fields = ('id', 'portfolio', 'operation_type', 'product', 'amount', 'price', 'timestamp')
        read_only_fields = ('id', 'timestamp')

class CurrencySerializer(serializers.ModelSerializer):
    """Сериализатор для модели валюты (Currency).

    Обрабатывает данные о доступных в системе валютах.
    
    Атрибуты:
        model (Currency): Модель валюты
        fields (tuple): Поля модели для сериализации
        read_only_fields (tuple): Поля, доступные только для чтения
    
    Поля:
        id (int): Уникальный идентификатор валюты (только для чтения)
        name (str): Полное название валюты (например, 'Доллар США')
        short_name (str): Краткое обозначение валюты (например, 'USD')
    
    Пример использования:
        # Добавление новой валюты
        serializer = CurrencySerializer(data={
            'name': 'Евро',
            'short_name': 'EUR'
        })
        if serializer.is_valid():
            currency = serializer.save()
    """
    class Meta:
        model = Currency
        fields = ('id', 'name', 'short_name')
        read_only_fields = ('id',)

class RateSerializer(serializers.ModelSerializer):
    """Сериализатор для модели курса валют (Rate).

    Обрабатывает данные о текущих курсах валют в системе.
    
    Атрибуты:
        model (Rate): Модель курса валют
        fields (tuple): Поля модели для сериализации
        read_only_fields (tuple): Поля, доступные только для чтения
    
    Поля:
        id (int): Уникальный идентификатор записи курса (только для чтения)
        cost (decimal): Текущая стоимость валюты
        timestamp (datetime): Время последнего обновления курса (автоматически)
    
    Пример использования:
        # Обновление курса валюты
        serializer = RateSerializer(rate, data={'cost': 76.25})
        if serializer.is_valid():
            updated_rate = serializer.save()
    """
    class Meta:
        model = Rate
        fields = ('id', 'cost', 'timestamp')
        read_only_fields = ('id', 'timestamp')

class CurrencyHistorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели истории курсов валют (CurrencyHistory).

    Обрабатывает исторические данные об изменениях курсов валют.
    
    Атрибуты:
        model (CurrencyHistory): Модель истории курсов
        fields (tuple): Поля модели для сериализации
        read_only_fields (tuple): Поля, доступные только для чтения
    
    Поля:
        id (int): Уникальный идентификатор записи истории (только для чтения)
        currency (int): ID валюты, для которой сохраняется история (внешний ключ)
    
    Пример использования:
        # Создание записи в истории курсов
        serializer = CurrencyHistorySerializer(data={'currency': currency_id})
        if serializer.is_valid():
            history_entry = serializer.save()
    """
    class Meta:
        model = CurrencyHistory
        fields = ('id', 'currency')
        read_only_fields = ('id',)