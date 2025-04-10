from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, TemplateView, UpdateView
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import Currency
from .forms import *


class HomeView(TemplateView):
    template_name = 'home.html'


class RegisterView(FormView):
    template_name = 'register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('app:login')

    def form_valid(self, form):
        user = form.save(commit=False)

        user.set_password(form.cleaned_data['password1'])
        user.save()

        return super().form_valid(form)


class LoginView(FormView):
    template_name = 'login.html'
    form_class = LoginForm
    success_url = reverse_lazy('app:account')

    def form_valid(self, form):
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']

        user = authenticate(self.request,
                            email=email,
                            password=password)

        if user is not None:
            login(self.request,
                  user)

            response = redirect(self.get_success_url())

            refresh = RefreshToken.for_user(user)

            response.set_cookie('access_token', str(refresh.access_token), httponly=True)

            return response

        form.add_error(None, "Invalid credentials")

        return self.form_invalid(form)


class LogoutView(View):
    success_url = reverse_lazy('app:login')

    def get(self, request):
        logout(request)

        response = redirect(str(self.success_url))
        response.delete_cookie('access_token')

        return response


class AccountView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = ProfileUpdateForm
    template_name = 'account.html'
    success_url = reverse_lazy('app:account')

    def get_object(self, queryset=None):
        return self.request.user


# class ChangePasswordView(LoginRequiredMixin, FormView):
#     template_name = 'auth/change_password.html'
#     form_class = PasswordChangeForm
#     success_url = reverse_lazy('profile')
#
#     def form_valid(self, form):
#         user = self.request.user
#         old_password = form.cleaned_data['old_password']
#         new_password = form.cleaned_data['new_password']
#
#         if not user.check_password(old_password):
#             form.add_error('old_password', "Wrong password")
#             return self.form_invalid(form)
#
#         user.set_password(new_password)
#         user.save()
#         return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get(self, request, *args, **kwargs):
        context = {}

        context['currencies'] = Currency.objects.all()

        return render(request,
                      self.template_name,
                      context)
