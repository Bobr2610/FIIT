from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Account


class RegisterForm(UserCreationForm):
    class Meta:
        model = Account
        fields = ['username']


class LoginForm(AuthenticationForm):
    class Meta:
        model = Account
        fields = ['username', 'password']
