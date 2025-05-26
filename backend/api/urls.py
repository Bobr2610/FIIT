from django.urls import path
from .views import *

app_name = 'api'

urlpatterns = [
    path('auth/register/', AuthViewSet.as_view({
        'post': 'register'
    }), name='auth-register'),
    path('auth/login/', AuthViewSet.as_view({
        'post': 'login'
    }), name='auth-login'),
    path('auth/logout/', AuthViewSet.as_view({
        'post': 'logout'
    }), name='auth-logout'),
    path('auth/refresh/', AuthViewSet.as_view({
        'post': 'refresh'
    }), name='auth-refresh'),
    path('auth/telegram/link/', AuthViewSet.as_view({
        'post': 'telegram_link'
    }), name='auth-telegram-link'),
    path('auth/telegram/verify/', AuthViewSet.as_view({
        'post': 'telegram_verify'
    }), name='auth-telegram-verify'),
    path('auth/telegram/status/', AuthViewSet.as_view({
        'get': 'telegram_status'
    }), name='auth-telegram-status'),

    path('accounts/me/', AccountViewSet.as_view({
        'get': 'me',
        'patch': 'update'
    }), name='account-me'),
    path('accounts/me/change-password/', AccountViewSet.as_view({
        'post': 'change_password'
    }), name='account-change-password'),

    path('portfolios/', PortfolioViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='portfolio-list'),
    path('portfolios/<int:pk>/', PortfolioViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='portfolio-detail'),
    path('portfolios/<int:pk>/currencies/', PortfolioViewSet.as_view({
        'get': 'currencies'
    }), name='portfolio-currencies'),
    path('portfolios/<int:pk>/buy/', PortfolioViewSet.as_view({
        'post': 'buy'
    }), name='portfolio-buy'),
    path('portfolios/<int:pk>/sell/', PortfolioViewSet.as_view({
        'post': 'sell'
    }), name='portfolio-sell'),
    path('portfolios/<int:pk>/operations/', PortfolioViewSet.as_view({
        'get': 'operations'
    }), name='portfolio-operations'),
    path('portfolios/<int:pk>/watches/', PortfolioViewSet.as_view({
        'get': 'watches'
    }), name='portfolio-watches'),

    path('operations/', OperationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='operation-list'),
    path('operations/<int:pk>/', OperationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='operation-detail'),

    path('currencies/', CurrencyViewSet.as_view({
        'get': 'list'
    }), name='currency-list'),
    path('currencies/<int:pk>/', CurrencyViewSet.as_view({
        'get': 'retrieve'
    }), name='currency-detail'),
    path('currencies/<int:pk>/rates/', CurrencyViewSet.as_view({
        'get': 'rates'
    }), name='currency-rates'),

    path('rates/', RateViewSet.as_view({
        'get': 'list'
    }), name='rate-list'),
    path('rates/<int:pk>/', RateViewSet.as_view({
        'get': 'retrieve'
    }), name='rate-detail'),

    path('watches/', WatchViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='watch-list'),
    path('watches/<int:pk>/', WatchViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='watch-detail'),
]
