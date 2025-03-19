from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import views as auth_views
from django.shortcuts import render
from django.views import generic, View


class AccountView(View, LoginRequiredMixin):
    template_name = 'account/account.html'

    login_url = "/login/"

    def get(self, request):
        return render(request, self.template_name)


class LoginView(auth_views.LoginView):
    template_name = 'account/login.html'
