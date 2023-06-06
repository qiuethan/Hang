"""
ICS4U
Paul Chen
This module contains serializers for various models related to user authentication and friend requests in a Django application.
"""

import urllib.parse

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, validators

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


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new User and associated Profile.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'username': {'validators': [validators.UniqueValidator(queryset=User.objects.all())]},
            'email': {'validators': [validators.UniqueValidator(queryset=User.objects.all())]}
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

    def validate_code(self, code):
        """
        Validate the Google login code.

        Arguments:
          code (str): The Google login code.

        Returns:
          str: The unquoted Google login code.
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
        redirect_uri = 'https://hang-coherentboi.vercel.app/auth'
        return GoogleAuthenticationToken.generate_token_from_code(code=validated_data["code"],
                                                                  redirect_uri=redirect_uri)


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
          EmailAuthenticationToken: The created EmailAuthenticationTokeninstance.
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
