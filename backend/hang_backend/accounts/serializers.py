import hashlib
import random
import string
from datetime import datetime, timezone, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from rest_framework import serializers, validators
from rest_framework.relations import PrimaryKeyRelatedField

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
        fields = ("user", "profile_picture", "is_verified")


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
    """
    Serializer for a friend request object. It should be used to serialize sent friend requests, as it does not show
    whether the request has been declined.
    """
    from_user = PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    to_user = PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user")

    def create(self, validated_data):
        """Generates a friend request object."""
        from_user = self.context["request"].user
        to_user = validated_data["to_user"]

        if from_user == to_user:
            raise serializers.ValidationError("Cannot send a friend request to yourself.")

        if from_user.userdetails.friends.filter(id=to_user.id).exists():
            raise serializers.ValidationError("User is already a friend.")

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already exists.")

        # Checks for existing friend request -> if `to_user` has already sent a friend request to `from_user`.
        existing_friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user)

        if existing_friend_request.exists() and not existing_friend_request.get().declined:
            raise serializers.ValidationError("This user has already sent you a friend request.")

        elif existing_friend_request.exists():
            existing_friend_request.delete()

        friend_request = FriendRequest(from_user=from_user, to_user=to_user)
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


class SendEmailSerializer(serializers.Serializer):
    """Serializer for SendEmailView."""

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
    """Serializer for VerifyEmailView."""
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
