from django.urls import path

from .views import *


app_name = 'api'

urlpatterns = [
    path('account/register/', RegisterView.as_view(), name='register'),
    path('account/login/', LoginView.as_view(), name='login'),
    path('account/logout/', LogoutView.as_view(), name='logout'),
    path('account/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('account/update-profile/', UpdateProfileView.as_view(), name='update-profile'),
    path('account/me/', UserDetailsView.as_view(), name='user-details'),
]
