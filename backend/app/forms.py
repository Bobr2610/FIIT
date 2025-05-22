from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from api.models import Account


class AccountForm(forms.ModelForm):
    """
    Форма для управления информацией аккаунта пользователя.
    Включает поля для имени пользователя, email и Telegram.
    """
    email = forms.EmailField(
        required=False,
        label='Email'
    )
    telegram = forms.CharField(
        required=False,
        label='Telegram'
    )

    class Meta:
        model = Account
        fields = ['username', 'email', 'telegram']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Введите имя пользователя'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Введите email'
            }),
            'telegram': forms.TextInput(attrs={
                'placeholder': 'Введите username в Telegram'
            })
        }

    def save(self, commit=True):
        """
        Сохраняет информацию аккаунта в базу данных.
        Если commit=True, изменения сохраняются немедленно.
        """
        account = super(AccountForm, self).save(commit=False)
        if commit:
            account.save()
        return account


class ChangePasswordForm(forms.Form):
    """
    Форма для смены пароля пользователя.
    Включает поля для старого пароля, нового пароля и подтверждения нового пароля.
    """
    old_password = forms.CharField(
        label='Текущий пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите текущий пароль'
        })
    )
    new_password = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите новый пароль'
        })
    )
    new_password_check = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Повторите новый пароль'
        })
    )

    error_messages = {
        'password_mismatch': 'Пароли не совпадают.',
        'password_incorrect': 'Неверный текущий пароль.',
        'password_too_short': 'Пароль должен содержать минимум 8 символов.',
        'password_too_common': 'Этот пароль слишком простой.',
        'password_entirely_numeric': 'Пароль не может состоять только из цифр.'
    }

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect',
            )
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if len(new_password) < 8:
            raise forms.ValidationError(
                self.error_messages['password_too_short'],
                code='password_too_short',
            )
        if new_password.isdigit():
            raise forms.ValidationError(
                self.error_messages['password_entirely_numeric'],
                code='password_entirely_numeric',
            )
        return new_password

    def clean_new_password_check(self):
        password1 = self.cleaned_data.get('new_password')
        password2 = self.cleaned_data.get('new_password_check')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        """
        Сохраняет новый пароль пользователя.
        """
        password = self.cleaned_data['new_password']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class RegisterForm(UserCreationForm):
    """
    Форма для регистрации пользователя.
    Включает поля для имени пользователя, email и пароля.
    """
    email = forms.EmailField(
        required=True,
        label='Email'
    )

    class Meta:
        model = Account
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Введите имя пользователя'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Введите email'
            })
        }


class LoginForm(forms.Form):
    """
    Форма для входа пользователя.
    Использует поля email и пароль для аутентификации.
    """
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'autofocus': True,
            'placeholder': 'Введите email'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Введите пароль'
        })
    )

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
