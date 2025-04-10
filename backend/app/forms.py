from django.contrib.auth.forms import SetPasswordMixin
from django import forms

from api.models import Account


class RegisterForm(forms.ModelForm):
    password1, password2 = SetPasswordMixin.create_password_fields()

    class Meta:
        model = Account
        fields = ['email', 'username']


class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput)
    new_password = forms.CharField(widget=forms.PasswordInput)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ['email', 'username', 'telegram']
