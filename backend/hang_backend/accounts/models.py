import hashlib
import json
import uuid
from datetime import datetime, timezone, timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import models
from google.oauth2 import id_token
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from rest_framework.exceptions import ValidationError

from google.auth.transport import requests as google_requests
from calendars.models import ManualCalendar, ImportedCalendar
from hang_backend import settings


class EmailAuthToken(models.Model):
    token = models.CharField(max_length=64, primary_key=True)  # Token is stored as SHA256 hash.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, user):
        random_string = str(uuid.uuid4())
        token_id = EmailAuthToken.hash_token(random_string)
        token = cls(token=token_id, user=user)
        token.save()

        send_mail("Hang Email Verification Token",
                  f"Your email verification token is {random_string}. This token will stay valid for 24 hours.",
                  settings.EMAIL_HOST_USER,
                  [token.user.email])

        return token

    def verify(self):
        if self.user.userdetails.is_verified:
            raise ValidationError("User is already verified.")

        if self.is_expired():
            raise ValidationError("Token expired.")

        self.user.userdetails.is_verified = True
        self.user.userdetails.save()

        self.delete()

    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def is_expired(self):
        return datetime.now(timezone.utc) - self.created_at > timedelta(days=1)


class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_friend_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_friend_requests")
    declined = models.BooleanField(default=False)

    @classmethod
    def create_friend_request(cls, from_user, to_user):
        friend_request = cls(from_user=from_user, to_user=to_user)
        friend_request.save()
        return friend_request

    @staticmethod
    def validate_friend_request(from_user, to_user):
        if from_user == to_user:
            raise ValidationError("Cannot send a friend request to yourself.")

        if from_user.userdetails.friends.filter(id=to_user.id).exists():
            raise ValidationError("User is already a friend.")

        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            raise ValidationError("Friend request already exists.")

        existing_friend_request = FriendRequest.objects.filter(from_user=to_user, to_user=from_user)
        if existing_friend_request.exists() and not existing_friend_request.get().declined:
            raise ValidationError("This user has already sent you a friend request.")

    def accept_friend_request(self):
        self.from_user.userdetails.add_friend(self.to_user)
        self.delete()

    def decline_friend_request(self):
        self.declined = True
        self.save()


class UserDetails(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.CharField(max_length=200, default="default profile pic change this later")
    is_verified = models.BooleanField(default=False)
    about_me = models.TextField(default="")

    friends = models.ManyToManyField(User, related_name="+")
    blocked_users = models.ManyToManyField(User, related_name="+")

    @staticmethod
    def create_user_and_associated_objects(username, email, password):
        user = User.objects.create_user(username, email, password)

        UserDetails.objects.create(user=user)
        ManualCalendar.objects.create(user=user)
        ImportedCalendar.objects.create(user=user)

        return user

    @staticmethod
    def authenticate_user(email, password, user_should_be_verified=True):
        user = authenticate(email=email, password=password)
        if not user or not user.is_active:
            raise ValidationError("Incorrect Credentials.")

        if user.userdetails.is_verified != user_should_be_verified:
            if user.userdetails.is_verified:
                raise ValidationError("User is already verified.")
            else:
                raise ValidationError("User is not verified.")
        return user

    def block_user(self, user_to_block):
        if self.user == user_to_block:
            raise ValidationError("Cannot block yourself.")
        self.blocked_users.add(user_to_block)

    def unblock_user(self, user_to_unblock):
        self.blocked_users.remove(user_to_unblock)

    def add_friend(self, user_to_add):
        self.friends.add(user_to_add)
        user_to_add.userdetails.friends.add(self.user)

    def remove_friend(self, user_to_remove):
        self.friends.remove(user_to_remove)
        user_to_remove.userdetails.friends.remove(self.user)


class GoogleAuthenticationToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=1024)
    last_generated = models.DateTimeField(default=datetime.now)

    @staticmethod
    def get_flow(redirect_uri):
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
        flow = GoogleAuthenticationToken.get_flow(redirect_uri)
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return authorization_url

    @classmethod
    def generate_token_from_code(cls, code, redirect_uri):
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
        refresh_threshold = 3600  # Set the time threshold for refreshing the token (in seconds)
        elapsed_time = (datetime.now(timezone.utc) - self.last_generated).total_seconds()
        return elapsed_time >= refresh_threshold

    def refresh_access_token(self):
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
