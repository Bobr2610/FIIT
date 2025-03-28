from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView

from .forms import *


class HomeView(TemplateView):
    template_name = 'home.html'


class AccountView(LoginRequiredMixin, TemplateView):
    template_name = 'account.html'

    login_url = 'login/'


class RegisterView(FormView):
    template_name = 'register.html'

    form_class = RegisterForm

    success_url = '/account'

    def post(self, request, *args, **kwargs):
        form = RegisterForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        form.save()

        return redirect(self.get_success_url())


class LoginView(auth_views.LoginView):
    template_name = 'login.html'

    form_class = LoginForm

    next_page = '/account'


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    template_name = 'logout.html'

    next_page = '/account'


class DashboardView(TemplateView):
    template_name = 'dashboard.html'
