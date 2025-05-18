from django.contrib import admin

from .models import *


admin.site.register(Account)
admin.site.register(Portfolio)
admin.site.register(CurrencyBalance)
admin.site.register(Operation)
admin.site.register(Currency)
admin.site.register(Rate)
admin.site.register(Watch)
