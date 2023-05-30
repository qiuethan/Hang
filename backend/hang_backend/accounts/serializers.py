import urllib.parse

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, validators

from .models import EmailAuthenticationToken, FriendRequest, Profile, \
    GoogleAuthenticationToken


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model. Converts User objects into JSON.
    """

    class Meta:
        model = User
        fields = ("id", "username", "email")
        read_only_fields = ("id", "username", "email")


class ProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the Profile model. Converts Profile objects into JSON.
    """
    user = UserSerializer()

    class Meta:
        model = Profile
        fields = ("user", "profile_picture", "is_verified", "about_me")
        read_only_fields = ("user", "is_verified")


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for the registration view. Validates user registration data.
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
        Creates a new User object from validated registration data.
        """
        return Profile.create_user_and_associated_objects(username=validated_data["username"],
                                                          email=validated_data["email"],
                                                          password=validated_data["password"])


class LoginSerializer(serializers.Serializer):
    """
    Serializer for the login view. Validates user login data.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        """
        Validates the user's email and password.
        """
        return {"user": Profile.authenticate_user(email=data["email"], password=data["password"])}


class LoginWithGoogleSerializer(serializers.Serializer):
    """
    Serializer for Google login. Validates the Google OAuth2 code.
    """
    code = serializers.CharField()

    def validate_code(self, code):
        """
        Decodes the Google OAuth2 code.
        """
        return urllib.parse.unquote(code)

    def create(self, validated_data):
        """
        Generates a Google OAuth2 token from the validated code.
        """
        redirect_uri = 'http://localhost:3000/auth'
        return GoogleAuthenticationToken.generate_token_from_code(code=validated_data["code"],
                                                                  redirect_uri=redirect_uri)


class EmailAuthenticationTokenSerializer(serializers.Serializer):
    """
    Serializer for email authentication. Validates the user's email and password.
    """
    email = serializers.EmailField()
    password = serializers.CharField()

    def create(self, validated_data):
        """
        Creates a new EmailAuthenticationToken for the user.
        """
        return EmailAuthenticationToken.create(user=validated_data["user"])

    def validate(self, data):
        """
        Validates the user's email and password.
        """
        return {"user": Profile.authenticate_user(email=data["email"],
                                                  password=data["password"],
                                                  user_should_be_verified=False)}


class FriendRequestSentSerializer(serializers.ModelSerializer):
    """
    Serializer for sent friend requests. Validates the friend request data.
    """

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user")
        read_only_fields = ("from_user",)

    def create(self, validated_data):
        """
        Creates a new FriendRequest object from the validated data.
        """
        return FriendRequest.create_friend_request(from_user=self.context["request"].user,
                                                   to_user=validated_data["to_user"])

    def validate(self, data):
        """
        Validates the friend request data.
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
    Serializer for received friend requests. Converts FriendRequest objects into JSON.
    """

    class Meta:
        model = FriendRequest
        fields = ("from_user", "to_user", "declined")
        read_only_fields = ("from_user", "to_user", "declined")
