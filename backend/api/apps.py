from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    # def ready(self):
    #     from .data.currencies import CURRENCIES
    #     from .data.rates import RATES

    #     from .models import Currency, Rate

    #     for currency in CURRENCIES:
    #         Currency.objects.get_or_create(
    #             name=currency['name'],
    #             defaults={
    #                 'short_name': currency['short_name'],
    #                 'description': currency['description'],
    #             }
    #         )

    #     for rate in RATES:
    #         currency_id = Currency.objects.get(name=rate['currency'])

    #         Rate.objects.get_or_create(
    #             currency=currency_id,
    #             defaults={
    #                 'cost': rate['cost'],
    #                 'timestamp': rate['timestamp'],
    #             }
    #         )
