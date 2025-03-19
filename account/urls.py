from django.urls import path

from .views import AccountView, LoginView

app_name = 'account'

urlpatterns = [
    path('', AccountView.as_view(), name='account'),
    path('login/', LoginView.as_view(), name='login')
]
