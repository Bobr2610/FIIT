from django.db import models


class Currency(models.Model):
    name = models.CharField(max_length=64)
    short_name = models.CharField(max_length=3)

    def __str__(self):
        return self.short_name


class Rate(models.Model):
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    price = models.FloatField()
    datetime = models.DateTimeField()

    def __str__(self):
        return self.currency.name
