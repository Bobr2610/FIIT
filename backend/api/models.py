from django.db import models
from django.contrib.auth.models import AbstractUser


class Account(AbstractUser):
    telegram_chat_id = models.BigIntegerField(null=True, blank=True, unique=True)

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'account'
        db_table_comment = 'User Account'
        verbose_name = 'Account'
        verbose_name_plural = 'Accounts'


class TelegramVerificationLink(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='telegram_links')
    code = models.CharField(max_length=32, unique=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        # TODO: replace to link
        return f'{self.user.username} {self.code}'

    class Meta:
        db_table = 'telegram_verification_link'
        db_table_comment = 'Telegram Verification Links'
        verbose_name = 'Telegram Verification Link'
        verbose_name_plural = 'Telegram Verification Links'


class Portfolio(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    balance = models.PositiveIntegerField()
    currencies = models.ManyToManyField('CurrencyBalance', related_name='portfolios', blank=True)
    operations = models.ManyToManyField('Operation', related_name='portfolios', blank=True)
    notify_threshold = models.FloatField(null=True, blank=True)
    watches = models.ManyToManyField('Watch', related_name='portfolios', blank=True)

    def __str__(self):
        return f'{self.account.username} {self.balance}'

    class Meta:
        db_table = 'portfolio'
        db_table_comment = 'Portfolio Of User'
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'


class CurrencyBalance(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.portfolio} {self.currency} {self.amount}'

    class Meta:
        db_table = 'currency_balance'
        db_table_comment = 'Currency Balance In Portfolio'
        verbose_name = 'Currency Balance'
        verbose_name_plural = 'Currency Balances'


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
        verbose_name = 'Operation'
        verbose_name_plural = 'Operations'


class Currency(models.Model):
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=128)
    description = models.TextField()

    def __str__(self):
        return f'{self.name} {self.short_name}'

    class Meta:
        db_table = 'currency'
        db_table_comment = 'Currencies'
        verbose_name = 'Currency'
        verbose_name_plural = 'Currencies'


class Rate(models.Model):
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    cost = models.PositiveIntegerField()
    timestamp = models.DateTimeField(db_index=True)

    def __str__(self):
        return f'{self.currency} {self.cost} {self.timestamp}'

    class Meta:
        db_table = 'rate'
        db_table_comment = 'Rates Of Currencies'
        verbose_name = 'Rate'
        verbose_name_plural = 'Rates'


class Watch(models.Model):
    portfolio = models.ForeignKey('Portfolio', on_delete=models.CASCADE)
    currency = models.ForeignKey('Currency', on_delete=models.CASCADE)
    notify_time = models.TimeField()

    def __str__(self):
        return f'{self.portfolio} {self.currency} {self.notify_time}'

    class Meta:
        db_table = 'watch'
        db_table_comment = 'Watches Of Currencies'
        verbose_name = 'Watch'
        verbose_name_plural = 'Watches'
