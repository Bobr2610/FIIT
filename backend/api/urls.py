from django.urls import path

from .views import *

app_name = 'api'

urlpatterns = [
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('users/me/', UserViewSet.as_view({'get': 'me'}), name='user-me'),
    path('users/me/update/', UserViewSet.as_view({'post': 'update_profile'}), name='user-update'),

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
