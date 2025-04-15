from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, SetPasswordMixin
from api.models import Account


class AccountForm(forms.ModelForm):
    """
    Form for managing user account information.
    Includes fields for username and email.
    """
    email = forms.EmailField(required=False)  # Field for user's email address

    class Meta:
        model = Account
        fields = ['username', 'email']  # Fields included in the form

    def save(self, commit=True):
        """
        Saves the account information to the database.
        If commit is True, the changes are saved immediately.
        """
        account = super(AccountForm, self).save(commit=False)
        if commit:
            account.save()  # Save the account instance
        return account


class RegisterForm(UserCreationForm):
    """
    Form for user registration.
    Includes fields for username, email and password.
    """
    email = forms.EmailField(required=True)

    class Meta:
        model = Account
        fields = ['username', 'email']  # Fields included in the registration form


class LoginForm(forms.Form):
    """
    Form for user login.
    Uses email and password fields for authentication.
    """
    email = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput())

    error_messages = {
        'invalid_login': "Недопустимая комбинация адреса эл. почты и пароля.",
        'inactive': "Этот аккаунт неактивен.",
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email is not None and password:
            self.user_cache = authenticate(self.request,
                                        email=email,
                                        password=password)
            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    self.error_messages['inactive'],
                    code='inactive',
                )
        return self.cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    Includes fields for username and email.
    """
    email = forms.EmailField(required=False)  # Field for user's email address

    class Meta:
        model = Account
        fields = ['username', 'email']  # Fields included in the form

    def save(self, commit=True):
        """
        Saves the profile information to the database.
        If commit is True, the changes are saved immediately.
        """
        profile = super(ProfileUpdateForm, self).save(commit=False)
        if commit:
            profile.save()  # Save the profile instance
        return profile
