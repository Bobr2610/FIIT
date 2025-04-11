from django.db import models
from django.contrib.auth.models import User


# TODO
class Account(User):
    """Модель аккаунта пользователя.

    Расширяет стандартную модель пользователя Django (User), добавляя дополнительные поля.

    Атрибуты:
        username (str): Имя пользователя (наследуется от User)
        email (str): Email пользователя (наследуется от User)
        telegram (URLField): Ссылка на Telegram пользователя
    """
    telegram = models.URLField()

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'account'
        db_table_comment = 'User account'


class Portfolio(models.Model):
    """Модель портфеля пользователя.

    Представляет собой портфель инвестиций, принадлежащий определенному аккаунту.

    Атрибуты:
        account (ForeignKey): Связь с моделью Account, указывает на владельца портфеля
    """
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.account.name # ???

    class Meta:
        db_table = 'portfolio'
        db_table_comment = 'Portfolio of user'


class Operation(models.Model):
    """Модель операции в портфеле.

    Представляет собой операцию покупки или продажи в портфеле пользователя.

    Атрибуты:
        portfolio (ForeignKey): Связь с портфелем, в котором совершена операция
        operation_type (str): Тип операции (покупка/продажа)
        product (str): Название продукта/валюты
        amount (int): Количество купленных/проданных единиц
        price (int): Цена за единицу
        timestamp (DateTime): Время совершения операции
    """
    OperationType = models.TextChoices('OperationType', 'BUY SELL')

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=128, choices=OperationType)
    product = models.CharField(max_length=128)
    amount = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    # TODO
    def __str__(self):
        return "..."

    class Meta:
        db_table = 'operation'
        db_table_comment = 'Operations in portfolio'


class Currency(models.Model):
    """Модель валюты.

    Представляет информацию о валюте в системе.

    Атрибуты:
        name (str): Полное название валюты
        short_name (str): Краткое обозначение валюты (например, USD, EUR)
    """
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=128)

    def __str__(self):
        return self.short_name

    class Meta:
        db_table = 'currency'
        db_table_comment = 'Currencies'


class CurrencyHistory(models.Model):
    """Модель истории курсов валюты.

    Хранит историческую информацию об изменениях курса валюты.

    Атрибуты:
        currency (ForeignKey): Связь с валютой, для которой хранится история
    TODO: Добавить поле rates для хранения исторических значений курса
    """
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    # TODO: Реализовать хранение исторических значений курса
    # rates = ???

    class Meta:
        db_table = 'currency_history'
        db_table_comment = 'History of currency rate'


class Rate(models.Model):
    cost = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rate'
        db_table_comment = 'Rate of currency in concrete time'

