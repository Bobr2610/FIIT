from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView
from rest_framework_simplejwt.tokens import RefreshToken
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from django.core.cache import cache
from django.utils import timezone

from api.serializers import *
from .forms import *


class HomeView(TemplateView):
    template_name = 'home.html'


class AccountView(LoginRequiredMixin, FormView):
    template_name = 'account.html'
    form_class = AccountForm
    success_url = reverse_lazy('app:account')
    login_url = 'app:login'

    def get_initial(self):
        serializer = AccountSerializer(self.request.user)

        return serializer.data

    def form_valid(self, form):
        user = self.request.user
        user.username = form.cleaned_data['username']
        user.email = form.cleaned_data['email']
        user.save()

        return super().form_valid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    template_name = 'change_password.html'
    form_class = ChangePasswordForm
    success_url = reverse_lazy('app:account')
    login_url = 'app:login'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user

        return kwargs

    def form_valid(self, form):
        user = self.request.user

        if user.check_password(form.cleaned_data['old_password']):
            user.set_password(form.cleaned_data['new_password'])
            user.save()

            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('app:login')

    def form_valid(self, form):
        user = form.save()
        
        Portfolio.objects.create(
            account=user,
            balance=settings.PORTFOLIO_BALANCE
        )

        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('app:account')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request

        return kwargs

    def form_valid(self, form):
        user = authenticate(
            request=self.request,
            email=form.cleaned_data['email'],
            password=form.cleaned_data['password']
        )

        if user is not None:
            login(self.request, user)

            refresh = RefreshToken.for_user(user)

            response = redirect(self.get_success_url())
            response.set_cookie('access_token', str(refresh.access_token), httponly=True)

            return response
        else:
            return self.form_invalid(form)


class LogoutView(LoginRequiredMixin, View):
    success_url = reverse_lazy('app:login')
    login_url = 'app:login'

    def get(self, request):
        logout(request)

        response = redirect(str(self.success_url))
        response.delete_cookie('access_token')

        return response


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = 'app:login'

    def get(self, request, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, account=request.user)
        serializer = PortfolioSerializer(portfolio)

        currencies = CurrencyBalance.objects.filter(portfolio=portfolio)
        currency_balance_serializer = CurrencyBalanceSerializer(currencies, many=True)

        actives = 0
        for currency_balance in currencies:
            current_rate = currency_balance.currency.rate_set.latest('-timestamp')
            actives += currency_balance.amount * current_rate.cost

        total_value = portfolio.balance + actives
        cache_key = f'portfolio_value_{portfolio.id}'
        previous_value = cache.get(cache_key)
        
        change_percent = None
        if previous_value is not None:
            change_percent = ((total_value - previous_value) / previous_value) * 100

        operations = Operation.objects.filter(portfolio=portfolio)
        operation_serializer = OperationSerializer(operations, many=True)

        watches = Watch.objects.filter(portfolio=portfolio)
        watch_serializer = WatchSerializer(watches, many=True)

        currencies = Currency.objects.all()
        currency_serializer = CurrencySerializer(currencies, many=True)

        chart_data = {}
        for currency in currencies:
            rates = Rate.objects.filter(currency=currency).order_by('-timestamp')
            rate_serializer = RateSerializer(rates, many=True)

            chart_data[currency.short_name] = {
                'labels': [rate['timestamp'] for rate in rate_serializer.data],
                'values': [float(rate['cost']) for rate in rate_serializer.data]
            }

        context = {
            'portfolio': serializer.data,
            'currency_balances': currency_balance_serializer.data,
            'actives': actives,
            'total_value': total_value,
            'change_percent': change_percent,
            'operations': operation_serializer.data,
            'watches': watch_serializer.data,
            'buy_form': PortfolioOperationForm(),
            'sell_form': PortfolioOperationForm(),
            'watch_form': WatchForm(),
            'currencies': currency_serializer.data,
            'chart_data': chart_data
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        portfolio = get_object_or_404(Portfolio, account=request.user)

        if 'buy' in request.POST:
            return self._handle_buy(request, portfolio)
        elif 'sell' in request.POST:
            return self._handle_sell(request, portfolio)
        elif 'add_watch' in request.POST:
            return self._handle_add_watch(request, portfolio)

        return redirect('app:dashboard')

    def _handle_buy(self, request, portfolio):
        form = PortfolioOperationForm(request.POST)

        if form.is_valid():
            currency = form.cleaned_data['currency']
            amount = form.cleaned_data['amount']

            rate = Rate.objects.filter(currency=currency).latest('timestamp')
            price = rate.cost
            total_cost = price * amount

            if portfolio.balance >= total_cost:
                operation = Operation.objects.create(
                    portfolio=portfolio,
                    currency=currency,
                    amount=amount,
                    price=price,
                    operation_type='buy'
                )

                portfolio.balance -= total_cost
                portfolio.save()

                balance, created = CurrencyBalance.objects.get_or_create(
                    portfolio=portfolio,
                    currency=currency,
                    defaults={'amount': amount}
                )

                if not created:
                    balance.amount += amount
                    balance.save()

        return redirect('app:dashboard')

    def _handle_sell(self, request, portfolio):
        form = PortfolioOperationForm(request.POST)

        if form.is_valid():
            currency = form.cleaned_data['currency']
            amount = form.cleaned_data['amount']

            balance = get_object_or_404(CurrencyBalance, portfolio=portfolio, currency=currency)
            if balance.amount >= amount:
                rate = Rate.objects.filter(currency=currency).latest('timestamp')
                price = rate.cost
                total_cost = price * amount

                operation = Operation.objects.create(
                    portfolio=portfolio,
                    currency=currency,
                    amount=amount,
                    price=price,
                    operation_type='sell'
                )

                portfolio.balance += total_cost
                portfolio.save()

                balance.amount -= amount
                if balance.amount == 0:
                    balance.delete()
                else:
                    balance.save()

        return redirect('app:dashboard')

    def _handle_add_watch(self, request, portfolio):
        form = WatchForm(request.POST)

        if form.is_valid():
            watch = Watch.objects.create(
                portfolio=portfolio,
                currency=form.cleaned_data['currency'],
                notify_time=form.cleaned_data['notify_time']
            )

            portfolio.watches.add(watch)

            schedule, _ = CrontabSchedule.objects.get_or_create(
                hour=watch.notify_time.hour,
                minute=watch.notify_time.minute,
                day_of_week='*',
                day_of_month='*',
                month_of_year='*',
            )

            PeriodicTask.objects.create(
                name=f'notify-{watch.id}',
                task='api.tasks.notify_currency_rate',
                crontab=schedule,
                args=[watch.id],
                enabled=True
            )

        return redirect('app:dashboard')
