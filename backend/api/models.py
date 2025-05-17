from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    telegram = models.CharField(max_length=128)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'account'
        db_table_comment = 'User Account'


class Portfolio(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    balance = models.PositiveIntegerField()
    # TODO: add currencies
    operations = models.ManyToManyField('Operation', related_name='portfolios', blank=True)
    notify_threshold = models.FloatField(null=True, blank=True)
    watches = models.ManyToManyField('Watch', related_name='portfolios', blank=True)

    def __str__(self):
        return f'{self.account.username} {self.balance}'

    class Meta:
        db_table = 'portfolio'
        db_table_comment = 'Portfolio Of User'


class Operation(models.Model):
    OperationType = models.TextChoices('OperationType', 'BUY SELL')

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    operation_type = models.CharField(max_length=128, choices=OperationType)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.operation_type} {self.currency} {self.amount} * {self.price} -> {self.amount * self.price}"

    class Meta:
        db_table = 'operation'
        db_table_comment = 'Operations In Portfolio'


class Currency(models.Model):
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=128)
    description = models.TextField()

    def __str__(self):
        return f'{self.name} {self.short_name}'

    class Meta:
        db_table = 'currency'
        db_table_comment = 'Currencies'


class Rate(models.Model):
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    cost = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.currency} {self.cost} {self.timestamp}'

    class Meta:
        db_table = 'rate'
        db_table_comment = 'Rate Of Currency'


class Watch(models.Model):
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    # TODO: change notify time type?
    notify_time = models.FloatField()

    def __str__(self):
        return f'{self.portfolio} {self.currency} {self.notify_time}'

    class Meta:
        db_table = 'watch'
        db_table_comment = 'Watch Of Currency'
