import urllib.parse

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, validators

from .models import EmailAuthToken, FriendRequest, UserDetails, \
    GoogleAuthenticationToken


class UserSerializer(serializers.ModelSerializer):
    """Class that serializes a User into JSON."""

    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id", "username", "email")


class UserDetailsSerializer(serializers.ModelSerializer):
    """Class that serializes all a UserDetails object into JSON."""
    user = UserSerializer()

    class Meta:
        model = UserDetails
        fields = ("user", "profile_picture", "is_verified", "about_me")
        read_only_fields = ("user", "is_verified")


class FriendRequestReceivedSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user", "declined")
        read_only_fields = ("from_user", "to_user", "declined")


class FriendRequestSentSerializer(serializers.ModelSerializer):
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

        if from_user.userdetails.friends.filter(id=to_user.id).exists():
            raise serializers.ValidationError("User is already a friend.")

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise serializers.ValidationError("Friend request already exists.")

        existing_friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user)
        if existing_friend_request.exists() and not existing_friend_request.get().declined:
            raise serializers.ValidationError("This user has already sent you a friend request.")

        return data


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for RegisterView."""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'validators': [validate_password]},
            'username': {'validators': [validators.UniqueValidator(queryset=User.objects.all())]},
            'email': {'validators': [validators.UniqueValidator(queryset=User.objects.all())]}
        }

    def create(self, validated_data):
        """Generates `User` object from params"""
        return UserDetails.create_user_and_associated_objects(username=validated_data["username"],
                                                              email=validated_data["email"],
                                                              password=validated_data["password"])


class LoginSerializer(serializers.Serializer):
    """Serializer for LoginView."""

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        return {"user": UserDetails.authenticate_user(email=data["email"], password=data["password"])}


class LoginWithGoogleSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, code):
        return urllib.parse.unquote(code)

    def create(self, validated_data):
        redirect_uri = 'http://localhost:3000/profile'
        return GoogleAuthenticationToken.generate_token_from_code(code=validated_data["code"],
                                                                  redirect_uri=redirect_uri)


class SendEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        return {"user": UserDetails.authenticate_user(email=data["email"],
                                                      password=data["password"],
                                                      user_should_be_verified=False)}

    def create(self, validated_data):
        return EmailAuthToken.create(user=validated_data["user"])

# TODO: friend request logic, accounts rtws, notifs
