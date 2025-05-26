from django.conf import settings
from django.contrib.auth import login, logout
from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework_simplejwt.tokens import RefreshToken
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from datetime import timedelta
import secrets

from .serializers import *

class AuthViewSet(viewsets.GenericViewSet):
    def get_permissions(self):
        if self.action in ['logout', 'telegram_link']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_serializer_class(self):
        if self.action == 'register':
            return AuthRegisterSerializer
        elif self.action == 'login':
            return AuthLoginSerializer
        elif self.action in ['logout', 'refresh']:
            return AuthRefreshSerializer
        elif self.action == 'telegram_link':
            return AuthTelegramLinkSerializer
        elif self.action == 'telegram_verify':
            return AuthTelegramVerifySerializer

        return None

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.context['action'] = 'register'
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': AccountSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.context['action'] = 'login'
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']

        login(request, user)

        refresh = RefreshToken.for_user(user)

        return Response({
            'user': AccountSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })

    @action(detail=False, methods=['post'])
    def logout(self, request):
        try:
            refresh_token = request.data['refresh']

            token = RefreshToken(refresh_token)
            token.blacklist()

            logout(request)

            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        try:
            refresh_token = request.data['refresh']

            token = RefreshToken(refresh_token)

            return Response({
                'access': str(token.access_token),
            })
        except Exception as exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def telegram_link(self, request):
        code = secrets.token_urlsafe(24)

        link = TelegramVerificationLink.objects.create(
            user=request.user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        serializer = self.get_serializer(data={
            'link': f'https://t.me/{settings.TELEGRAM_BOT_USERNAME}?start={code}',
            'expires_at': link.expires_at
        })
        serializer.is_valid(raise_exception=True)

        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def telegram_verify(self, request):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        code = serializer.validated_data['code']
        chat_id = serializer.validated_data['chat_id']

        try:
            link = TelegramVerificationLink.objects.get(
                code=code,
                expires_at__gt=timezone.now()
            )

            if Account.objects.filter(telegram_chat_id=chat_id).exclude(id=link.user_id).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)

            user = link.user
            user.telegram_chat_id = chat_id
            user.save()

            link.delete()

            return Response(status=HTTP_200_OK)
        except TelegramVerificationLink.DoesNotExist:
            return Response(status=HTTP_400_BAD_REQUEST)


class AccountViewSet(viewsets.ModelViewSet):
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'patch', 'post']

    def get_queryset(self):
        return Account.objects.filter(id=self.request.user.id)

    def get_object(self):
        obj = super().get_object()

        if obj != self.request.user:
            raise PermissionDenied("Вы не можете управлять чужим аккаунтом")

        return obj

    def get_serializer_class(self):
        if self.action == 'update':
            return AccountUpdateSerializer
        elif self.action == 'change_password':
            return PasswordChangeSerializer

        return AccountSerializer

    @action(detail=False, methods=['get'])
    def me(self, request):
        serializer = self.get_serializer(request.user)

        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update(self, request):
        serializer = self.get_serializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(AccountSerializer(request.user).data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.context['user'] = request.user
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(status=status.HTTP_200_OK)


class PortfolioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(account=self.request.user)

    def get_object(self):
        obj = super().get_object()

        if obj.account != self.request.user:
            raise PermissionDenied("Вы не можете управлять чужим портфелем")

        return obj

    def get_serializer_class(self):
        if self.action in ['buy', 'sell']:
            return PortfolioOperationSerializer

        return PortfolioSerializer

    def perform_create(self, serializer):
        serializer.save(account=self.request.user)

    @action(detail=True, methods=['post'])
    def buy(self, request, pk=None):
        portfolio = self.get_object()
        serializer = PortfolioOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        currency = serializer.validated_data['currency']
        amount = serializer.validated_data['amount']
        
        try:
            current_rate = currency.rate_set.latest('timestamp')
            price = current_rate.cost
        except Rate.DoesNotExist:
            return Response(
                {"error": "Нет доступных курсов для этой валюты"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        total_cost = amount * price
        
        if portfolio.balance < total_cost:
            return Response(
                {"error": "Недостаточно средств на балансе"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        with transaction.atomic():
            operation = Operation.objects.create(
                operation_type='buy',
                portfolio=portfolio,
                currency=currency,
                amount=amount,
                price=price
            )
            
            portfolio.balance -= total_cost
            portfolio.save()
            
            currency_balance, created = CurrencyBalance.objects.get_or_create(
                portfolio=portfolio,
                currency=currency,
                defaults={'amount': amount}
            )
            
            if not created:
                currency_balance.amount += amount
                currency_balance.save()
            
            portfolio.operations.add(operation)
        
        return Response(OperationSerializer(operation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def sell(self, request, pk=None):
        portfolio = self.get_object()
        serializer = PortfolioOperationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        currency = serializer.validated_data['currency']
        amount = serializer.validated_data['amount']
        
        try:
            current_rate = currency.rate_set.latest('timestamp')
            price = current_rate.cost
        except Rate.DoesNotExist:
            return Response(
                {"error": "Нет доступных курсов для этой валюты"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            currency_balance = CurrencyBalance.objects.get(
                portfolio=portfolio,
                currency=currency
            )
        except CurrencyBalance.DoesNotExist:
            return Response(
                {"error": "У вас нет этой валюты"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if currency_balance.amount < amount:
            return Response(
                {"error": "Недостаточно валюты для продажи"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        total_value = amount * price
        
        with transaction.atomic():
            operation = Operation.objects.create(
                operation_type='sell',
                portfolio=portfolio,
                currency=currency,
                amount=amount,
                price=price
            )
            
            portfolio.balance += total_value
            portfolio.save()
            
            currency_balance.amount -= amount
            currency_balance.save()
            
            portfolio.operations.add(operation)
        
        return Response(OperationSerializer(operation).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def operations(self, request, pk=None):
        portfolio = self.get_object()

        operations = portfolio.operations.all()

        serializer = OperationSerializer(operations, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def watches(self, request, pk=None):
        portfolio = self.get_object()

        watches = portfolio.watches.all()

        serializer = WatchSerializer(watches, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def currencies(self, request, pk=None):
        portfolio = self.get_object()

        currency_balances = CurrencyBalance.objects.filter(portfolio=portfolio).select_related('currency')

        serializer = CurrencyBalanceSerializer(currency_balances, many=True)

        return Response(serializer.data)


class OperationViewSet(viewsets.ModelViewSet):
    serializer_class = OperationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Operation.objects.filter(portfolio__account=self.request.user)

    def get_object(self):
        obj = super().get_object()

        if obj.portfolio.account != self.request.user:
            raise PermissionDenied("Вы не можете управлять чужими операциями")

        return obj

    def perform_create(self, serializer):
        portfolio = serializer.validated_data['portfolio']

        if portfolio.account != self.request.user:
            raise PermissionDenied("Вы не можете создавать операции в чужом портфеле")

        serializer.save()


class CurrencyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['get'])
    def rates(self, request, pk=None):
        currency = self.get_object()

        rates = currency.rate_set.order_by('-timestamp')

        serializer = RateSerializer(rates, many=True)

        return Response(serializer.data)


class RateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Rate.objects.select_related('currency').order_by('-timestamp')

        short_name = self.request.query_params.get('short_name')

        if short_name:
            queryset = queryset.filter(currency__short_name=short_name)

        return queryset


class WatchViewSet(viewsets.ModelViewSet):
    serializer_class = WatchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watch.objects.filter(portfolio__account=self.request.user)

    def get_object(self):
        obj = super().get_object()

        if obj.portfolio.account != self.request.user:
            raise PermissionDenied("Вы не можете управлять чужими отслеживаемыми валютами")

        return obj

    def perform_create(self, serializer):
        portfolio = serializer.validated_data['portfolio']

        if portfolio.account != self.request.user:
            raise PermissionDenied("Вы не можете добавлять отслеживаемые валюты в чужой портфель")
        
        watch = serializer.save()
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

    def perform_destroy(self, instance):
        PeriodicTask.objects.filter(name=f'notify-{instance.id}').delete()

        instance.delete()
