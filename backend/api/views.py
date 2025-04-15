from django.contrib.auth import login
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (RegistrationSerializer, LoginSerializer,
                        ChangePasswordSerializer, AccountSerializer)


class RegisterView(APIView):
    """
    Регистрация нового пользователя.

    POST-запрос должен содержать:
    * username - имя пользователя
    * email - электронная почта
    * password1 - пароль
    * password2 - подтверждение пароля
    """
    permission_classes = []

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors,
                      status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Авторизация пользователя.

    POST-запрос должен содержать:
    * username - имя пользователя
    * password - пароль
    """
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)

            refresh = RefreshToken.for_user(user)

            response = Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })

            response.set_cookie('access_token',
                              str(refresh.access_token),
                              httponly=True)
            response.set_cookie('refresh_token',
                              str(refresh),
                              httponly=True)

            return response

        return Response(serializer.errors,
                      status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Выход пользователя из системы.

    POST-запрос должен содержать:
    * refresh - токен обновления для добавления в черный список
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as error:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    Изменение пароля пользователя.

    POST-запрос должен содержать:
    * old_password - текущий пароль
    * new_password - новый пароль
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user = request.user

            if not user.check_password(serializer.data['old_password']):
                return Response({
                    "error": "Неверный пароль"
                }, status=status.HTTP_400_BAD_REQUEST)

            user.set_password(serializer.data['new_password'])
            user.save()

            return Response(status=status.HTTP_200_OK)

        return Response(serializer.errors,
                      status=status.HTTP_400_BAD_REQUEST)


class UpdateProfileView(APIView):
    """
    Обновление профиля пользователя.

    POST-запрос может содержать:
    * username - новое имя пользователя
    * email - новая электронная почта
    * telegram - новая ссылка на Telegram
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AccountSerializer(request.user,
                                     data=request.data,
                                     partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors,
                      status=status.HTTP_400_BAD_REQUEST)


class UserDetailsView(APIView):
    """Получение информации о текущем пользователе."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = AccountSerializer(request.user)
        return Response(serializer.data)
