from django.contrib.auth import authenticate
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password

from .models import *


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ('email', 'username', 'password', 'password2', 'telegram')
        extra_kwargs = {
            'telegram': {'required': False}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = Account.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs['username'], password=attrs['password'])
        if not user:
            raise serializers.ValidationError('Неверные учетные данные')
        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Пароли не совпадают"})
        return attrs


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('email', 'username', 'telegram')
        extra_kwargs = {
            'email': {'required': False}
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'email', 'telegram', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class PortfolioSerializer(serializers.ModelSerializer):
    account = AccountSerializer(read_only=True)
    operations_count = serializers.SerializerMethodField()
    watches_count = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ('id', 'account', 'balance', 'notify_threshold', 
                 'operations_count', 'watches_count')
        read_only_fields = ('id',)

    def get_operations_count(self, obj):
        return obj.operations.count()

    def get_watches_count(self, obj):
        return obj.watches.count()


class CurrencySerializer(serializers.ModelSerializer):
    current_rate = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = ('id', 'name', 'short_name', 'description', 'current_rate')
        read_only_fields = ('id',)

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
