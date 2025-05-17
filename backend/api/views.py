from django.contrib.auth import login
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import *
from .serializers import *


class RegisterView(APIView):
    """
    Регистрация нового пользователя.

    POST-запрос должен содержать:
    * username - имя пользователя
    * email - электронная почта
    * password - пароль
    * password2 - подтверждение пароля
    * telegram - ссылка на Telegram (опционально)
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    Авторизация пользователя.

    POST-запрос должен содержать:
    * username - имя пользователя
    * password - пароль
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            login(request, user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    Выход пользователя из системы.

    POST-запрос должен содержать:
    * refresh - токен обновления для добавления в черный список
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {"error": "Требуется токен обновления"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(APIView):
    """
    Изменение пароля пользователя.

    POST-запрос должен содержать:
    * old_password - текущий пароль
    * new_password - новый пароль
    * new_password2 - подтверждение нового пароля
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"error": "Неверный пароль"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """
    Конечная точка API для управления пользователями.
    """
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Account.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Получение информации о текущем пользователе.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_profile(self, request):
        """
        Обновление профиля текущего пользователя.
        """
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    Конечная точка API для управления портфелями.
    """
    serializer_class = PortfolioSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(account=self.request.user)

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)

    @action(detail=True, methods=['get'])
    def operations(self, request, pk=None):
        """
        Получение списка операций в портфеле.
        """
        portfolio = self.get_object()
        operations = portfolio.operations.all()
        serializer = OperationSerializer(operations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def watches(self, request, pk=None):
        """
        Получение списка отслеживаемых валют в портфеле.
        """
        portfolio = self.get_object()
        watches = portfolio.watches.all()
        serializer = WatchSerializer(watches, many=True)
        return Response(serializer.data)


class OperationViewSet(viewsets.ModelViewSet):
    """
    Конечная точка API для управления операциями.
    """
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Operation.objects.filter(portfolio__account=self.request.user)

    def perform_create(self, serializer):
        portfolio = serializer.validated_data['portfolio']
        if portfolio.account != self.request.user:
            raise permissions.PermissionDenied(
                "Вы не можете создавать операции в чужом портфеле")
        serializer.save()


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Конечная точка API для просмотра информации о валютах.
    """
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def rates(self, request, pk=None):
        """
        Получение истории курсов валюты.
        """
        currency = self.get_object()
        rates = currency.rate_set.order_by('-timestamp')
        serializer = RateSerializer(rates, many=True)
        return Response(serializer.data)


class RateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Конечная точка API для просмотра курсов валют.
    """
    queryset = Rate.objects.all()
    serializer_class = RateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Rate.objects.select_related('currency').order_by('-timestamp')


class WatchViewSet(viewsets.ModelViewSet):
    """
    Конечная точка API для управления отслеживаемыми валютами.
    """
    serializer_class = WatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watch.objects.filter(portfolio__account=self.request.user)

    def perform_create(self, serializer):
        portfolio = serializer.validated_data['portfolio']
        if portfolio.account != self.request.user:
            raise permissions.PermissionDenied(
                "Вы не можете добавлять отслеживаемые валюты в чужой портфель")
        serializer.save()
