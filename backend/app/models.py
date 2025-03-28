from django.db import models
from django.contrib.auth.models import User


# TODO
class Account(User):
    # login = models.EmailField(unique=True)
    # password = models.CharField(max_length=128)
    telegram = models.URLField()

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'account'
        db_table_comment = 'User account'


class Portfolio(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    def __str__(self):
        return self.account.name # ???

    class Meta:
        db_table = 'portfolio'
        db_table_comment = 'Portfolio of user'


class Operation(models.Model):
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
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=128)

    def __str__(self):
        return self.short_name

    class Meta:
        db_table = 'currency'
        db_table_comment = 'Currencies'


class CurrencyHistory(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    # TODO
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

