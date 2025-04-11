"""Конфигурация URL-адресов для основного приложения.

Содержит маршруты для:
1. Веб-интерфейса (регистрация, вход, личный кабинет, дашборд)
2. REST API эндпоинтов (пользователи, счета, портфели, операции, валюты)

API эндпоинты доступны по префиксу /api/ и используют ViewSet'ы
для реализации стандартных CRUD операций.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *
from .api_views import (
    UserViewSet, AccountViewSet, PortfolioViewSet, OperationViewSet,
    CurrencyViewSet, CurrencyHistoryViewSet, RateViewSet
)

app_name = 'app'

# Регистрация API эндпоинтов через DefaultRouter
router = DefaultRouter()
router.register(r'api/users', UserViewSet)  # Управление пользователями
router.register(r'api/accounts', AccountViewSet)  # Управление аккаунтами
router.register(r'api/portfolios', PortfolioViewSet)  # Управление портфелями
router.register(r'api/operations', OperationViewSet)  # Управление операциями
router.register(r'api/currencies', CurrencyViewSet)  # Управление валютами
router.register(r'api/currency-history', CurrencyHistoryViewSet)  # История курсов валют
router.register(r'api/rates', RateViewSet)  # Текущие курсы валют

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('home/', HomeView.as_view(), name='home'),

    path('account/', AccountView.as_view(), name='account'),
    path('account/register/', RegisterView.as_view(), name='register'),
    path('account/login/', LoginView.as_view(), name='login'),
    path('account/logout/', LogoutView.as_view(), name='logout'),

    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    # Подключение URL-адресов API
    path('', include(router.urls)),  # Подключаем все API маршруты
]
