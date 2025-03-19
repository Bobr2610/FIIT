from django.contrib import admin

from .models import Currency, Rate


admin.site.register(Currency)
admin.site.register(Rate)
