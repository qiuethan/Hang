import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from rest_framework.exceptions import ValidationError

from hang_backend import settings
from notifications.models import Notification
from real_time_ws.models import RTWSSendMessageOnUpdate


class Profile(models.Model, RTWSSendMessageOnUpdate):
    """
    This model represents a user profile. It extends the Django User model and adds additional fields.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.CharField(max_length=2000,
                                       default="/static/media/logo.76ffd1144b342263116b472f0c0cff50.svg")
    is_verified = models.BooleanField(default=False)
    about_me = models.TextField(default="")

    friends = models.ManyToManyField(User, related_name="+")
    blocked_users = models.ManyToManyField(User, related_name="+")

    rtws_message_content = "profile"

    def get_rtws_users(self):
        return [self.user]

    @staticmethod
    def create_user_and_associated_objects(username, email, password):
        """
        This static method creates a new user and associated objects.
        """
        from calendars.models import ManualCalendar, ImportedCalendar

        user = User.objects.create_user(username, email, password)

        Profile.objects.create(user=user)
        ManualCalendar.objects.create(user=user)
        ImportedCalendar.objects.create(user=user)

        return user

    @staticmethod
    def authenticate_user(email, password, user_should_be_verified=True):
        """
        This static method authenticates a user using their email and password.
        """
        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
            raise ValidationError("Incorrect Credentials.")

        if user.profile.is_verified != user_should_be_verified:
            if user.profile.is_verified:
                raise ValidationError("User is already verified.")
            else:
                raise ValidationError("User is not verified.")
        return user

    def block_user(self, user_to_block):
        """
        This method allows a user to block another user.
        """
        if self.user == user_to_block:
            raise ValidationError("Cannot block yourself.")
        FriendRequest.objects.filter(from_user=user_to_block, to_user=self.user).delete()
        FriendRequest.objects.filter(from_user=self.user, to_user=user_to_block).delete()
        if user_to_block in self.friends.all():
            self.remove_friend(user_to_block)
        self.blocked_users.add(user_to_block)

    def unblock_user(self, user_to_unblock):
        """
        This method allows a user to unblock another user.
        """
        self.blocked_users.remove(user_to_unblock)

    def add_friend(self, user_to_add):
        """
        This method allows a user to add another user as a friend.
        """
        self.friends.add(user_to_add)
        user_to_add.profile.friends.add(self.user)

    def remove_friend(self, user_to_remove):
        """
        This method allows a user to remove another user from their friends list.
        """
        self.friends.remove(user_to_remove)
        user_to_remove.profile.friends.remove(self.user)


class GoogleAuthenticationToken(models.Model):
    """
    This model represents a Google authentication token.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=1024)
    last_generated = models.DateTimeField(default=datetime.now)

    @staticmethod
    def get_flow(redirect_uri):
        """
        This static method returns a Google OAuth2 flow object configured with the client's credentials.
        """
        flow = Flow.from_client_config(
            client_config={
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [redirect_uri],
                }
            },
            scopes=['https://www.googleapis.com/auth/calendar',
                    'https://www.googleapis.com/auth/userinfo.email',
                    'openid']
        )
        flow.redirect_uri = redirect_uri
        return flow

    @staticmethod
    def get_authorization_url(redirect_uri):
        """
        This static method returns the Google OAuth2 authorization URL.
        """
        flow = GoogleAuthenticationToken.get_flow(redirect_uri)
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return authorization_url

    @classmethod
    def generate_token_from_code(cls, code, redirect_uri):
        """
        This class method generates a Google OAuth2 token from an authorization code.
        """
        try:
            flow = cls.get_flow(redirect_uri)
            flow.fetch_token(code=code)

            if not flow.credentials:
                raise ValidationError("Access token not received")

            idinfo = id_token.verify_oauth2_token(flow.credentials.id_token,
                                                  google_requests.Request(),
                                                  settings.GOOGLE_CLIENT_ID)
            email = idinfo["email"]

            if not email:
                raise ValidationError("Email not received")

            if not User.objects.filter(email=email).exists():
                raise ValidationError("User doesn't exist")

            user = User.objects.get(email=email)

            if cls.objects.filter(user=user).exists():
                google_token = cls.objects.get(user=user)
                google_token.access_token = flow.credentials.token
                google_token.refresh_token = flow.credentials.refresh_token
                google_token.last_generated = datetime.now()
            else:
                google_token = cls.objects.create(user=user,
                                                  access_token=flow.credentials.token,
                                                  refresh_token=flow.credentials.refresh_token)

            google_token.save()

            return user

        except (json.JSONDecodeError, ValidationError, ValueError) as error:
            raise ValidationError(str(error))

    def needs_refresh(self):
        """
        This method checks if the Google OAuth2 token needs to be refreshed.
        """
        refresh_threshold = 3600  # Set the time threshold for refreshing the token (in seconds)
        elapsed_time = (datetime.now(timezone.utc) - self.last_generated).total_seconds()
        return elapsed_time >= refresh_threshold

    def refresh_access_token(self):
        """
        This method refreshes the Google OAuth2 access token.
        """
        if not self.needs_refresh():
            return
        credentials = Credentials.from_authorized_user_info(info={
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'token_uri': 'https://oauth2.googleapis.com/token'
        })

        credentials.refresh(google_requests.Request())
        new_token = credentials.token
        self.access_token = new_token
        self.last_generated = datetime.now(timezone.utc)
        self.save()


class EmailAuthenticationToken(models.Model):
    """
    This model represents an email authentication token.
    """
    token = models.CharField(max_length=64, primary_key=True)  # Token is stored as SHA256 hash.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, user):
        """
        This class method creates a new email authentication token for a user.
        """
        random_string = str(uuid.uuid4())
        token_id = EmailAuthenticationToken.hash_token(random_string)
        token = cls(token=token_id, user=user)
        token.save()

        send_mail("Hang Email Verification Token",
                  f"Your email verification token is {random_string}. This token will stay valid for 24 hours.",
                  settings.EMAIL_HOST_USER,
                  [token.user.email])

        return token

    def verify(self):
        """
        This method verifies the email authentication token.
        """
        if self.user.profile.is_verified:
            raise ValidationError("User is already verified.")

        if self.is_expired():
            raise ValidationError("Token expired.")

        self.user.profile.is_verified = True
        self.user.profile.save()

        self.delete()

    @staticmethod
    def hash_token(token):
        """
        This static method hashes the email authentication token.
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def is_expired(self):
        """
        This method checks if the email authentication token has expired.
        """
        return datetime.now(timezone.utc) - self.created_at > timedelta(days=1)


class FriendRequest(models.Model, RTWSSendMessageOnUpdate):
    """
    This model represents a friend request between two users.
    """
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_friend_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_friend_requests")
    declined = models.BooleanField(default=False)

    rtws_message_content = "friend_request"

    def get_rtws_users(self):
        return [self.from_user, self.to_user]

    @classmethod
    def create_friend_request(cls, from_user, to_user):
        """
        This class method creates a new friend request from one user to another.
        """
        if to_user in from_user.profile.blocked_users.all() or \
                from_user in to_user.profile.blocked_users.all():
            raise ValidationError(
                "Friend request creation failed. Cannot create a friend request when one user is blocked.")
        Notification.create_notification(user=to_user,
                                         title=from_user.username,
                                         description=f"{from_user.username} has sent you a friend request")
        friend_request = cls(from_user=from_user, to_user=to_user)
        friend_request.save()
        return friend_request

    def accept_friend_request(self):
        """
        This method allows a user to accept a friend request.
        """
        self.from_user.profile.add_friend(self.to_user)
        self.delete()

    def decline_friend_request(self):
        """
        This method allows a user to decline a friend request.
        """
        self.declined = True
        self.save()
