from django import forms
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
    Inherits from UserCreationForm to include username and password fields.
    """
    class Meta:
        model = Account
        fields = ['username']  # Fields included in the registration form


class LoginForm(AuthenticationForm):
    """
    Form for user login.
    Inherits from AuthenticationForm to include username and password fields.
    """
    class Meta:
        model = Account
        fields = ['username', 'password']  # Fields included in the login form
