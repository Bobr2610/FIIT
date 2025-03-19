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


class CurrenciesView(generic.ListView):
    template_name = "/index.html"
    context_object_name = "latest_question_list"

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by("-pub_date")[:5]
