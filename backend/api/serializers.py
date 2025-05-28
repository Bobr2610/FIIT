from django.contrib.auth import authenticate

from rest_framework import serializers

from .models import *


class AuthLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        write_only_fields = ('password',)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])

        if not user:
            raise serializers.ValidationError("Неверное имя пользователя или пароль")

        data['user'] = user

        return data


class AuthRegisterSerializer(serializers.ModelSerializer):
    password_check = serializers.CharField()

    class Meta:
        model = Account
        fields = ('username', 'email', 'password', 'password_check')
        write_only_fields = ('password', 'password_check')

    def validate(self, data):
        if data['password'] != data['password_check']:
            raise serializers.ValidationError("Пароли не совпадают")

        if Account.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({
                'username': 'Пользователь с таким именем уже существует'
            })

        if Account.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({
                'email': 'Пользователь с таким email уже существует'
            })

        return data

    def create(self, validated_data):
        validated_data.pop('password_check')

        user = Account.objects.create_user(**validated_data)

        return user


class AuthRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class AuthTelegramVerifySerializer(serializers.Serializer):
    code = serializers.CharField()
    chat_id = serializers.IntegerField()


class AuthTelegramLinkSerializer(serializers.Serializer):
    link = serializers.CharField()
    expires_at = serializers.DateTimeField()


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'telegram_chat_id')
        read_only_fields = ('id', 'telegram_chat_id')


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('username', 'email')


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    new_password_check = serializers.CharField()

    class Meta:
        write_only_fields = ('old_password', 'new_password', 'new_password_check')

    def validate(self, data):
        if data['new_password'] != data['new_password_check']:
            raise serializers.ValidationError("Новые пароли не совпадают")

        return data

    def save(self, **kwargs):
        user = self.context['user']

        if not user.check_password(self.validated_data['old_password']):
            raise serializers.ValidationError("Неверный текущий пароль")

        user.set_password(self.validated_data['new_password'])
        user.save()

        return user


# TODO: replace counts to objects?
class PortfolioSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    operations_count = serializers.SerializerMethodField()
    watches_count = serializers.SerializerMethodField()
    currencies_count = serializers.SerializerMethodField()
    total_balance = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ('id', 'account', 'balance', 'notify_threshold',
                  'operations_count', 'watches_count', 'currencies_count',
                  'total_balance')
        read_only_fields = ('id',)

    def get_operations_count(self, obj):
        return obj.operations.count()

    def get_watches_count(self, obj):
        return obj.watches.count()

    def get_currencies_count(self, obj):
        return CurrencyBalance.objects.filter(portfolio=obj).count()

    def get_total_balance(self, obj):
        total = obj.balance
        currency_balances = CurrencyBalance.objects.filter(portfolio=obj).select_related('currency')
        
        for balance in currency_balances:
            try:
                current_rate = balance.currency.rate_set.latest('timestamp')
                total += balance.amount * current_rate.cost
            except Rate.DoesNotExist:
                continue
                
        return total


class PortfolioOperationSerializer(serializers.Serializer):
    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        source='currency'
    )
    amount = serializers.FloatField()


class CurrencySerializer(serializers.ModelSerializer):
    current_rate = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = ('id', 'name', 'short_name', 'description',
                  'current_rate')
        read_only_fields = fields

    def get_current_rate(self, obj):
        latest_rate = obj.rate_set.order_by('-timestamp').first()

        return latest_rate.cost if latest_rate else None


class RateSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        write_only=True,
        source='currency'
    )
    timestamp = serializers.DateTimeField(format='%Y-%m-%d')

    class Meta:
        model = Rate
        fields = ('id', 'currency', 'currency_id', 'cost', 'timestamp')
        read_only_fields = ('id', 'timestamp')


class CurrencyBalanceSerializer(serializers.ModelSerializer):
    currency = CurrencySerializer(read_only=True)
    current_price = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = CurrencyBalance
        fields = ('currency', 'amount', 'current_price', 'total_value')
        read_only_fields = fields

    def get_current_price(self, obj):
        try:
            return obj.currency.rate_set.latest('timestamp').cost
        except Rate.DoesNotExist:
            return None

    def get_total_value(self, obj):
        try:
            current_price = obj.currency.rate_set.latest('timestamp').cost

            return obj.amount * current_price
        except Rate.DoesNotExist:
            return None


class OperationSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer(read_only=True)
    portfolio_id = serializers.PrimaryKeyRelatedField(
        queryset=Portfolio.objects.all(),
        write_only=True,
        source='portfolio'
    )
    currency = CurrencySerializer()
    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        write_only=True,
        source='currency'
    )
    total_amount = serializers.SerializerMethodField()

    class Meta:
        model = Operation
        fields = ('id', 'portfolio', 'portfolio_id', 'operation_type',
                  'currency', 'currency_id', 'amount', 'price',
                  'total_amount', 'timestamp')
        read_only_fields = ('id', 'timestamp')

    def get_total_amount(self, obj):
        return obj.amount * obj.price


class WatchSerializer(serializers.ModelSerializer):
    portfolio = PortfolioSerializer(read_only=True)
    portfolio_id = serializers.PrimaryKeyRelatedField(
        queryset=Portfolio.objects.all(),
        write_only=True,
        source='portfolio'
    )
    currency = CurrencySerializer(read_only=True)
    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        write_only=True,
        source='currency'
    )

    class Meta:
        model = Watch
        fields = ('id', 'portfolio', 'portfolio_id', 'currency',
                  'currency_id', 'notify_time')
        read_only_fields = ('id', )
