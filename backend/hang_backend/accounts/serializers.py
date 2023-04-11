import hashlib
import json
import random
import string
import urllib.parse
from datetime import datetime, timezone, timedelta

import requests
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from rest_framework import serializers, validators
from rest_framework.relations import PrimaryKeyRelatedField

from calendars.models import GoogleCalendarAccessToken
from hang_backend import settings
from .models import EmailAuthToken, FriendRequest, UserDetails


class UserSerializer(serializers.ModelSerializer):
    """Class that serializes a User into JSON."""
    id = serializers.IntegerField(default=None)
    username = serializers.CharField(default=None)
    email = serializers.EmailField(default=None)

    class Meta:
        model = User
        fields = ("id", "username", "email")

    def validate(self, data):
        qs = User.objects.filter(id=data["id"])
        if qs.count() == 0:
            raise serializers.ValidationError("User does not exist.")
        return qs.get()


class UserDetailsSerializer(serializers.ModelSerializer):
    """Class that serializes all a UserDetails object into JSON."""
    user = UserSerializer()

    class Meta:
        model = UserDetails
        fields = ("user", "profile_picture", "is_verified", "about_me")


class FriendRequestReceivedSerializer(serializers.ModelSerializer):
    """
    Serializer for a friend request object. It should be used to serialize received friend requests, as it shows
    whether the request has been declined.
    """
    from_user = PrimaryKeyRelatedField(queryset=User.objects.all())
    to_user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user", "declined")
        read_only_fields = ("from_user", "to_user", "declined")

    def update(self, instance, validated_data):
        # Declines a friend request.
        instance.declined = True
        instance.save()
        return instance


class FriendRequestSentSerializer(serializers.ModelSerializer):
    from_user = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    to_user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user")

    def validate(self, data):
        from_user = self.context["request"].user
        to_user = data["to_user"]

        if from_user == to_user:
            raise serializers.ValidationError("Cannot send a friend request to yourself.")

        if from_user.userdetails.friends.filter(id=to_user.id).exists():
            raise serializers.ValidationError("User is already a friend.")

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already exists.")

        existing_friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user)

        if existing_friend_request.exists() and not existing_friend_request.get().declined:
            raise serializers.ValidationError("This user has already sent you a friend request.")

        return data

    def create(self, validated_data):
        friend_request = FriendRequest(from_user=self.context["request"].user, to_user=validated_data["to_user"])
        friend_request.save()
        return friend_request


class RegisterSerializer(serializers.Serializer):
    """Serializer for RegisterView."""

    # Ensures that username and email are unique, and that the password is valid.
    username = serializers.CharField(validators=[validators.UniqueValidator(queryset=User.objects.all())],
                                     max_length=40)
    email = serializers.EmailField(validators=[validators.UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(validators=[validate_password], write_only=True)

    def create(self, validated_data):
        """Generates `User` object from params"""
        user = User.objects.create_user(validated_data["username"], validated_data["email"], validated_data["password"])
        user_details = UserDetails(user=user)
        user_details.save()
        return user

    def update(self, instance, validated_data):
        raise NotImplementedError


class LoginSerializer(serializers.Serializer):
    """Serializer for LoginView."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if not user or not user.is_active:
            raise serializers.ValidationError("Incorrect Credentials.")

        if not user.userdetails.is_verified:
            raise serializers.ValidationError("User is not verified.")

        return user

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class LoginWithGoogleSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, validated_data):
        code = urllib.parse.unquote(validated_data.get('code'))
        url = 'https://oauth2.googleapis.com/token'
        data = {
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': 'http://localhost:3000/auth',
            'access_type': 'offline',
            'grant_type': 'authorization_code',
        }

        try:
            response = requests.post(url, data=data)
            response_json = response.json()
            access_token = response_json.get('access_token')
            refresh_token = response_json.get('refresh_token')

            if not access_token:
                raise serializers.ValidationError("Access token not received")

            url = f'https://www.googleapis.com/oauth2/v3/userinfo?access_token={access_token}'
            response = requests.get(url)
            response_json = response.json()
            email = response_json.get('email')

            if not email:
                raise serializers.ValidationError("Email not received")

            if not User.objects.filter(email=email).exists():
                raise serializers.ValidationError("User doesn't exist")

            user = User.objects.get(email=email)

            if GoogleCalendarAccessToken.objects.filter(user=user).exists():
                google_token = GoogleCalendarAccessToken.objects.get(user=user)
                google_token.access_token = access_token
                google_token.refresh_token = refresh_token
                google_token.last_generated = datetime.now()
            else:
                google_token = GoogleCalendarAccessToken.objects.create(
                    user=user, access_token=access_token, refresh_token=refresh_token)

            google_token.save()

            return user

        except (json.JSONDecodeError, serializers.ValidationError) as error:
            raise serializers.ValidationError(str(error))

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError


class SendEmailSerializer(serializers.Serializer):
    """Serializer for SendVerificationEmailView."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)

        if not user or not user.is_active:
            raise serializers.ValidationError("Incorrect Credentials.")

        if user.userdetails.is_verified:
            raise serializers.ValidationError("User is already verified.")

        return data

    def create(self, validated_data):
        def generate_random_string():
            """Generates a sequence of random characters for EmailAuthToken."""
            return "".join([random.choice(string.ascii_letters) for _ in range(20)])

        ss = generate_random_string()
        while EmailAuthToken.objects.filter(id=ss).exists():
            ss = generate_random_string()

        # Generates `EmailAuthToken` object.
        token = EmailAuthToken(id=hashlib.sha256(ss.encode("utf-8")).hexdigest(),
                               user=User.objects.get(email=validated_data["email"]))
        token.save()

        # Sends email with verification token.
        send_mail("Hang Email Verification Token",
                  f"Your email verification token is {ss}. This token will stay valid for 24 hours.",
                  settings.EMAIL_HOST_USER,
                  [token.user.email])

        return token

    def update(self, instance, validated_data):
        raise NotImplementedError


class VerifyEmailSerializer(serializers.Serializer):
    """Serializer for VerifyEmailVerificationTokenView."""
    token = serializers.CharField()

    def validate(self, data):
        data["token"] = hashlib.sha256(data["token"].encode("utf-8")).hexdigest()

        if not EmailAuthToken.objects.filter(id=data["token"]).exists():
            raise serializers.ValidationError("Token does not exist.")

        token = EmailAuthToken.objects.get(id=data["token"])
        if token.user.userdetails.is_verified:
            raise serializers.ValidationError("User is already verified.")

        if datetime.now(timezone.utc) - token.created_at > timedelta(days=1):
            raise serializers.ValidationError("Token expired.")

        return token.user

    def create(self, validated_data):
        raise NotImplementedError

    def update(self, instance, validated_data):
        raise NotImplementedError
