from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import *


class AuthLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])

        if not user:
            raise serializers.ValidationError('Неверные учетные данные')

        attrs['user'] = user

        return attrs


class AuthRegisterSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(required=True)
    telegram = serializers.CharField(required=False)

    def validate(self, attrs):
        if Account.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Пользователь с таким именем уже существует"})
        if Account.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Пользователь с такой почтой уже существует"})

        return attrs

    def create(self, validated_data):
        user = Account.objects.create_user(**validated_data)

        return user


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'telegram', 'date_joined')
        read_only_fields = fields


class AccountUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('email', 'telegram')
        extra_kwargs = {
            'email': {'required': False},
            'telegram': {'required': False}
        }


class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})

        if not self.context['user'].check_password(attrs['old_password']):
            raise serializers.ValidationError({"old_password": "Неверный пароль"})

        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PortfolioSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    operations_count = serializers.SerializerMethodField()
    watches_count = serializers.SerializerMethodField()
    currencies_count = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ('id', 'account', 'balance', 'notify_threshold',
                  'operations_count', 'watches_count', 'currencies_count')
        read_only_fields = ('id', 'account')

    def get_operations_count(self, obj):
        return obj.operations.count()

    def get_watches_count(self, obj):
        return obj.watches.count()

    def get_currencies_count(self, obj):
        return CurrencyBalance.objects.filter(portfolio=obj).count()


class PortfolioOperationSerializer(serializers.Serializer):
    currency_id = serializers.PrimaryKeyRelatedField(
        queryset=Currency.objects.all(),
        source='currency'
    )
    amount = serializers.DecimalField(max_digits=20, decimal_places=8)


class CurrencySerializer(serializers.ModelSerializer):
    current_rate = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = ('id', 'name', 'short_name', 'description', 'current_rate')
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
    currency = CurrencySerializer(read_only=True)
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
        read_only_fields = ('id',)
