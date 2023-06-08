"""
ICS4U
Paul Chen
This module defines the serializers for the accounts package.
"""
import re
import urllib.parse

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError

from .models import EmailVerificationToken, FriendRequest, Profile, GoogleAuthenticationToken


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the built-in User model."""

    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id", "username", "email")


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for the User model including extra fields provided by the Profile model."""
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ("user", "profile_picture", "is_verified", "about_me")
        read_only_fields = ("user", "is_verified")


def validate_username(value):
    """
    Check that the username only contains alphanumeric characters.
    """
    if not re.match('^[a-zA-Z0-9]*$', value):
        raise ValidationError('Username can only contain alphanumeric characters.')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for accounts.views.RegisterView. Creates a user based on a username, email, and password."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'username': {'validators': [validators.UniqueValidator(queryset=User.objects.all()), validate_username]},
            'email': {'validators': [validators.UniqueValidator(queryset=User.objects.all())]},
            'password': {'write_only': True, 'validators': [validate_password]},
        }

    def create(self, validated_data):
        return Profile.create_user_and_associated_objects(username=validated_data["username"],
                                                          email=validated_data["email"],
                                                          password=validated_data["password"])


class LoginSerializer(serializers.Serializer):
    """Serializer for accounts.views.LoginView. Returns an existing user given an email and password."""
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        return {"user": Profile.authenticate_user(email=data["email"], password=data["password"])}


class LoginWithGoogleSerializer(serializers.Serializer):
    """
    Serializer for accounts.views.LoginWithGoogleView. Returns an existing user given a Google
    authorization code and a redirect uri. The redirect uri field is necessary to support multiple
    different possible redirects with the same method.
    """
    code = serializers.CharField()
    redirect_uri = serializers.ChoiceField(choices=["http://localhost:3000/auth", "http://localhost:3000/profile",
                                                    "https://hang-coherentboi.vercel.app/auth",
                                                    "https://hang-coherentboi.vercel.app/profile"])

    def validate_code(self, code):
        """Prepares the code by fixing escape sequences."""
        return urllib.parse.unquote(code)

    def create(self, validated_data):
        return GoogleAuthenticationToken.generate_token_from_code(code=validated_data["code"],
                                                                  redirect_uri=validated_data["redirect_uri"])


class EmailVerificationTokenSerializer(serializers.Serializer):
    """
    Serializer for creating an EmailAuthenticationToken.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def create(self, validated_data):
        return EmailVerificationToken.create(user=validated_data["user"])

    def validate(self, data):
        return {"user": Profile.authenticate_user(email=data["email"],
                                                  password=data["password"],
                                                  user_should_be_verified=False)}


class FriendRequestSentSerializer(serializers.ModelSerializer):
    """
    Serializer for accounts.views.FriendRequestSentViewSet. This serializer should be used when the sender of the
    friend request is the current user, as it hides whether the friend request has been declined.
    """

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user")
        read_only_fields = ("from_user",)

    def create(self, validated_data):
        return FriendRequest.create_friend_request(from_user=self.context["request"].user,
                                                   to_user=validated_data["to_user"])

    def validate(self, data):
        from_user = self.context["request"].user
        to_user = data["to_user"]

        if from_user == to_user:
            raise serializers.ValidationError("Cannot send a friend request to yourself.")
        if from_user.profile.friends.filter(id=to_user.id).exists():
            raise serializers.ValidationError("User is already a friend.")
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already exists.")
        existing_friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user)
        if existing_friend_request.exists() and not existing_friend_request.get().declined:
            raise serializers.ValidationError("This user has already sent you a friend request.")

        return data


class FriendRequestReceivedSerializer(serializers.ModelSerializer):
    """
    Serializer for accounts.views.FriendRequestReceivedViewSet. This serializer should be used when the receiver
    of the friend request is the current user, as it shows whether the friend request has been declined.
    """

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user", "declined")
        read_only_fields = ("from_user", "to_user", "declined")
