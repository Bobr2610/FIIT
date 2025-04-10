from django.contrib.auth import authenticate
from rest_framework import serializers

from .models import *


class AccountRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Account
        fields = ('email', 'username', 'password')

    def create(self, validated_data):
        user = Account.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )

        return user


class AccountLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])

        if not user:
            raise serializers.ValidationError("Invalid credentials")

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class UpdateUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = Account
        fields = ('email', 'username', 'telegram')
        extra_kwargs = {
            'email': {'required': False}
        }
