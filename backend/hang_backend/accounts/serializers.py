"""
ICS4U
Paul Chen
This module contains serializers for the models defined in the models.py.
"""
import re
import urllib.parse

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, validators
from rest_framework.exceptions import ValidationError

from .models import EmailAuthenticationToken, FriendRequest, Profile, GoogleAuthenticationToken


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id", "username", "email")


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model.

    Attributes:
      user (UserSerializer): Serializer for the associated User model.
    """
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
    """
    Serializer for registering a new User and associated Profile.
    """

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'username': {'validators': [validators.UniqueValidator(queryset=User.objects.all()), validate_username]},
            'email': {'validators': [validators.UniqueValidator(queryset=User.objects.all())]},
            'password': {'write_only': True, 'validators': [validate_password]},
        }

    def create(self, validated_data):
        """
        Create a new User and associated Profile.

        Arguments:
          validated_data (dict): Validated data for creating a new User and Profile.

        Returns:
          Profile: The created Profile instance.
        """
        return Profile.create_user_and_associated_objects(username=validated_data["username"],
                                                          email=validated_data["email"],
                                                          password=validated_data["password"])


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validate the login data.

        Arguments:
          data (dict): Data for login.

        Returns:
          dict: A dictionary containing the authenticated User instance.
        """
        return {"user": Profile.authenticate_user(email=data["email"], password=data["password"])}


class LoginWithGoogleSerializer(serializers.Serializer):
    """
    Serializer for logging in with Google.
    """
    code = serializers.CharField()
    redirect_uri = serializers.ChoiceField(choices=["http://localhost:3000/auth", "http://localhost:3000/profile",
                                                    "https://hang-coherentboi.vercel.app/auth",
                                                    "https://hang-coherentboi.vercel.app/profile"])

    def validate_code(self, code):
        """
        Prepares the code by fixing escape sequences.

        Arguments:
          code (str): The Google login code.

        Returns:
          str: The fixed Google login code.
        """
        return urllib.parse.unquote(code)

    def create(self, validated_data):
        """
        Create a GoogleAuthenticationToken from the validated code.

        Arguments:
          validated_data (dict): Validated data containing the Google login code.

        Returns:
          GoogleAuthenticationToken: The created GoogleAuthenticationToken instance.
        """
        return GoogleAuthenticationToken.generate_token_from_code(code=validated_data["code"],
                                                                  redirect_uri=validated_data["redirect_uri"])


class EmailAuthenticationTokenSerializer(serializers.Serializer):
    """
    Serializer for creating an EmailAuthenticationToken.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def create(self, validated_data):
        """
        Create an EmailAuthenticationToken.

        Arguments:
          validated_data (dict): Validated data for creating an EmailAuthenticationToken.

        Returns:
          EmailAuthenticationToken: The created EmailAuthenticationToken instance.
        """
        return EmailAuthenticationToken.create(user=validated_data["user"])

    def validate(self, data):
        """
        Validate the data for creating an EmailAuthenticationToken.

        Arguments:
          data (dict): Data for creating an EmailAuthenticationToken.

        Returns:
          dict: A dictionary containing the authenticated User instance.
        """
        return {"user": Profile.authenticate_user(email=data["email"],
                                                  password=data["password"],
                                                  user_should_be_verified=False)}


class FriendRequestSentSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a FriendRequest.
    """

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user")
        read_only_fields = ("from_user",)

    def create(self, validated_data):
        """
        Create a FriendRequest.

        Arguments:
          validated_data (dict): Validated data for creating a FriendRequest.

        Returns:
          FriendRequest: The created FriendRequest instance.
        """
        return FriendRequest.create_friend_request(from_user=self.context["request"].user,
                                                   to_user=validated_data["to_user"])

    def validate(self, data):
        """
        Validate the data for creating a FriendRequest.

        Arguments:
          data (dict): Data for creating a FriendRequest.

        Returns:
          dict: The validated data.

        Raises:
          ValidationError: If the from_user is the same as the to_user, if the to_user is already a friend of the from_user,
                           if a FriendRequest already exists between the from_user and to_user, or if the to_user has already
                           sent a FriendRequest to the from_user that has not been declined.
        """
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
    Serializer for received FriendRequests.
    """

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user", "declined")
        read_only_fields = ("from_user", "to_user", "declined")
