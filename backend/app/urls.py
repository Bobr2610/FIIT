from django.urls import path

from .views import *

app_name = 'app'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('home/', HomeView.as_view(), name='home'),

    path('account/', AccountView.as_view(), name='account'),
    path('account/register/', RegisterView.as_view(), name='register'),
    path('account/login/', LoginView.as_view(), name='login'),
    path('account/logout/', LogoutView.as_view(), name='logout'),
    path('account/change-password/', ChangePasswordView.as_view(), name='change-password'),

    path('portfolio/', PortfolioView.as_view(), name='portfolio'),

    path('market/', MarketView.as_view(), name='market')
]
