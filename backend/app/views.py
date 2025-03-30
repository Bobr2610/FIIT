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

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to display the account management page.
        Pre-fills the form with the current user's information.
        """
        form = AccountForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to update the user's account information.
        Validates the form and saves changes if valid.
        Redirects to the account page upon successful update.
        """
        form = AccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  # Save the updated user information
            return redirect('app:account')  # Redirect to the account page
        return render(request, self.template_name, {'form': form})  # Re-render the form with errors if invalid


class RegisterView(FormView):
    template_name = 'register.html'

    form_class = RegisterForm

    success_url = '/account'

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests for user registration.
        Validates the registration form and saves the new user if valid.
        Redirects to the account page upon successful registration.
        """
        form = RegisterForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})  # Re-render the form with errors if invalid

        form.save()  # Save the new user

        return redirect(self.get_success_url())  # Redirect to the success URL


class LoginView(auth_views.LoginView):
    template_name = 'login.html'

    form_class = LoginForm

    next_page = '/account'


class LogoutView(LoginRequiredMixin, auth_views.LogoutView):
    template_name = 'logout.html'

    next_page = '/account/login/'


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'
    login_url = '/account/login/'
