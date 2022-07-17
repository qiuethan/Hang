from datetime import datetime, timezone, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from .models import EmailAuthToken


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')


# Register Serializer
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def validate_username(self, data):
        if User.objects.filter(username=data).exists():
            raise serializers.ValidationError("The username must be unique.")
        return data

    def validate_email(self, data):
        if User.objects.filter(email=data).exists():
            raise serializers.ValidationError("The email must be unique.")
        return data

    def validate_password(self, data):
        validate_password(password=data, user=User)
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['username'], validated_data['email'], validated_data['password'])
        return user


# Login Serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            if not user.settings.is_verified:
                raise serializers.ValidationError("User is not verified.")
            return user
        raise serializers.ValidationError("Incorrect Credentials.")


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            if user.settings.is_verified:
                raise serializers.ValidationError("User is already verified.")
            return user
        raise serializers.ValidationError("Incorrect Credentials.")


class VerifyEmailSerializer(serializers.Serializer):
    token = serializers.CharField()

    def validate(self, data):
        if not EmailAuthToken.objects.filter(id=data['token']).exists():
            raise serializers.ValidationError("Token does not exist.")
        token = EmailAuthToken.objects.get(id=data['token'])
        if token.user.settings.is_verified:
            raise serializers.ValidationError("User is already verified.")
        if datetime.now(timezone.utc) - token.created_at > timedelta(days=1):
            raise serializers.ValidationError("Token expired.")
        return token.user
