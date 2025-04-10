from django.contrib import admin

from .models import *


admin.site.register(Account)
admin.site.register(Portfolio)
admin.site.register(Operation)
admin.site.register(Currency)
admin.site.register(CurrencyHistory)
admin.site.register(Rate)
