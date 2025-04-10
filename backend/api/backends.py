from django.contrib.auth.backends import ModelBackend

from .models import Account


class AuthBackend(ModelBackend):

    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = Account.objects.get(email=email)

            if user.check_password(password):
                return user

            return None
        except Account.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Account.objects.get(pk=user_id)
        except Account.DoesNotExist:
            return None
