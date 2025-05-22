from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import messages

from api.models import Currency, Portfolio, Rate

from .forms import *


class HomeView(TemplateView):
    """
    Представление для главной страницы.
    """
    template_name = 'home/index.html'


class AccountView(LoginRequiredMixin, TemplateView):
    """
    Представление для управления настройками аккаунта пользователя.
    Включает изменение имени, email, telegram и пароля.
    """
    template_name = 'account/index.html'
    login_url = 'app:login'

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET запросы для отображения страницы настроек.
        Заполняет формы текущей информацией пользователя.
        """
        account_form = AccountForm(instance=request.user)
        password_form = ChangePasswordForm(user=request.user)
        return render(request, self.template_name, {
            'account_form': account_form,
            'password_form': password_form
        })

    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST запросы для обновления настроек.
        Определяет тип формы и обрабатывает соответственно.
        """
        if 'change_password' in request.POST:
            password_form = ChangePasswordForm(request.user, request.POST)
            if password_form.is_valid():
                password_form.save()
                return redirect('app:account')
            account_form = AccountForm(instance=request.user)
        else:
            form = AccountForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('app:account')
            account_form = form
            password_form = ChangePasswordForm(user=request.user)

        return render(request, self.template_name, {
            'account_form': account_form,
            'password_form': password_form
        })


class ChangePasswordView(LoginRequiredMixin, FormView):
    """
    Представление для смены пароля пользователя.
    """
    template_name = 'account/change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('app:account')
    login_url = 'app:login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class RegisterView(FormView):
    """
    Представление для регистрации нового пользователя.
    Использует RegisterForm.
    """
    template_name = 'account/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('app:login')

    def form_valid(self, form):
        """
        Обрабатывает успешную валидацию формы.
        Создает нового пользователя и перенаправляет на страницу входа.
        """
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password1'])
        user.save()
        return super().form_valid(form)


class LoginView(FormView):
    """
    Представление для входа пользователя.
    Использует LoginForm.
    """
    template_name = 'account/login.html'
    form_class = LoginForm
    success_url = reverse_lazy('app:account')

    def get_form_kwargs(self):
        """
        Добавляет текущий запрос в форму.
        """
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        """
        Обрабатывает успешную валидацию формы.
        Выполняет вход пользователя и устанавливает JWT токен.
        """
        login(self.request, form.get_user())
        response = redirect(self.get_success_url())
        refresh = RefreshToken.for_user(form.get_user())
        response.set_cookie('access_token', str(refresh.access_token), httponly=True)
        return response


class LogoutView(LoginRequiredMixin, View):
    """
    Представление для выхода пользователя из системы.
    """
    success_url = reverse_lazy('app:login')
    login_url = 'app:login'

    def get(self, request):
        """
        Обрабатывает GET запросы для выхода пользователя.
        Удаляет сессию и JWT токен.
        """
        logout(request)
        response = redirect(str(self.success_url))
        response.delete_cookie('access_token')
        return response


class PortfolioView(LoginRequiredMixin, TemplateView):
    """
    Представление для просмотра портфеля пользователя.
    Показывает все активы пользователя и их текущую стоимость.
    """
    template_name = 'portfolio/index.html'
    login_url = 'app:login'

    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET запросы для отображения портфеля.
        Добавляет список активов пользователя в контекст.
        """
        context = {}
        portfolio = Portfolio.objects.filter(account=request.user)
        context['portfolio'] = portfolio
        return render(request, self.template_name, context)


class MarketView(LoginRequiredMixin, TemplateView):
    """
    Представление для просмотра рынка активов.
    Показывает список всех доступных активов с графиками.
    """
    template_name = 'market/index.html'
    login_url = 'app:login'
    
    def get(self, request, *args, **kwargs):
        """
        Обрабатывает GET запросы для отображения рынка.
        Добавляет список всех активов в контекст.
        """
        context = {}
        currencies = Currency.objects.all()
        rates = Rate.objects.all().order_by('-timestamp')
        
        # Подготавливаем данные для графиков
        chart_data = {}
        for currency in currencies:
            currency_rates = rates.filter(currency=currency)
            chart_data[currency.short_name] = {
                'labels': [rate.timestamp.strftime('%Y-%m-%d %H-%M-%S') for rate in currency_rates],
                'values': [float(rate.cost) for rate in currency_rates]
            }
        
        context['currencies'] = currencies
        context['chart_data'] = chart_data
        return render(request, self.template_name, context)
