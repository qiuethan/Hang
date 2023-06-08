"""
ICS4U
Paul Chen
This module defines the models for the accounts package.
"""

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
    Model that “extends” the default User model. When a User registers, a corresponding 
    Profile model is created for the User that contains extra information.

    Attributes:
      user (OneToOneField[User]): The user associated with this profile.
      profile_picture (CharField): The user's profile picture encoded as a string.
      is_verified (BooleanField): Whether the user's email is verified.
      about_me (TextField): The user's self-description.
      friends (ManyToManyField[User]): The user's friends.
      blocked_users (ManyToManyField[User]): The users blocked by this user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.CharField(max_length=200000,
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
        Creates a new user and associated objects (Profile, ManualCalendar, ImportedCalendar).

        Arguments:
          username (str): The username of the new user.
          email (str): The email of the new user.
          password (str): The password of the new user.

        Returns:
          User: The created user.
        """
        from calendars.models import ManualCalendar, ImportedCalendar  # We import here to avoid circular imports

        user = User.objects.create_user(username, email, password)

        Profile.objects.create(user=user)
        ManualCalendar.objects.create(user=user)
        ImportedCalendar.objects.create(user=user)

        return user

    @staticmethod
    def authenticate_user(email, password, user_should_be_verified=True):
        """
        Authenticates a user with the given email and password.

        Arguments:
          email (str): The email of the user.
          password (str): The password of the user.
          user_should_be_verified (bool): Whether the user should be verified.

        Returns:
          User: The authenticated user.
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
        Blocks a user.

        Arguments:
          user_to_block (User): The user to block.
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
        Unblocks a user.

        Arguments:
          user_to_unblock (User): The user to unblock.
        """
        self.blocked_users.remove(user_to_unblock)

    def add_friend(self, user_to_add):
        """
        Adds a user as a friend.

        Arguments:
          user_to_add (User): The user to add as a friend.
        """
        self.friends.add(user_to_add)
        user_to_add.profile.friends.add(self.user)

    def remove_friend(self, user_to_remove):
        """
        Removes a user from the friends list.

        Arguments:
          user_to_remove (User): The user to remove from the friends list.
        """
        self.friends.remove(user_to_remove)
        user_to_remove.profile.friends.remove(self.user)


class GoogleAuthenticationToken(models.Model):
    """
    Model that contains required tokens for Google authentication.
    Also provides utility methods that allow for token creation and management.

    Attributes:
      user (OneToOneField[User]): The user associated with this token.
      access_token (CharField): The access token.
      refresh_token (CharField): The refresh token.
      last_generated (DateTimeField): The time when the token was last generated.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=512)
    refresh_token = models.CharField(max_length=1024)
    last_generated = models.DateTimeField(default=datetime.now)

    @staticmethod
    def get_flow(redirect_uri):
        """
        Gets the OAuth2 flow for Google authentication.

        Arguments:
          redirect_uri (str): The redirect URI for the OAuth2 flow.

        Returns:
          Flow: The OAuth2 flow.
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
        Gets the authorization URL for Google authentication.

        Arguments:
          redirect_uri (str): The redirect URI for the OAuth2 flow.

        Returns:
          str: The authorization URL.
        """
        flow = GoogleAuthenticationToken.get_flow(redirect_uri)
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return authorization_url

    @classmethod
    def generate_token_from_code(cls, code, redirect_uri):
        """
        Using the authorization code obtained by the user, obtain the Google authentication tokens as well as
        user information.

        Arguments:
          code (str): The authorization code.
          redirect_uri (str): The redirect URI for the OAuth2 flow.

        Returns:
          User: The user associated with the generated token.
        """
        try:
            # Obtains the access token using the authorization code.
            flow = cls.get_flow(redirect_uri)
            flow.fetch_token(code=code)
            if not flow.credentials:
                raise ValidationError("Access token not received")

            # Obtain the user's information from the access token.
            idinfo = id_token.verify_oauth2_token(flow.credentials.id_token,
                                                  google_requests.Request(),
                                                  settings.GOOGLE_CLIENT_ID)
            email = idinfo["email"]

            # Verify that the output is as expected and that a user with the same email exists.
            if not email:
                raise ValidationError("Email not received")
            if not User.objects.filter(email=email).exists():
                raise ValidationError("User doesn't exist")

            user = User.objects.get(email=email)

            # If a corresponding GoogleAuthenticationToken object exists already, update it.
            if cls.objects.filter(user=user).exists():
                google_token = cls.objects.get(user=user)
                google_token.access_token = flow.credentials.token
                google_token.refresh_token = flow.credentials.refresh_token
                google_token.last_generated = datetime.now()
            # Otherwise create a new one.
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
        Checks if the token needs to be refreshed.

        Returns:
          bool: True if the token needs to be refreshed, False otherwise.
        """
        refresh_threshold = 3600  # Set the time threshold for refreshing the token (in seconds)
        elapsed_time = (datetime.now(timezone.utc) - self.last_generated).total_seconds()
        return elapsed_time >= refresh_threshold

    def refresh_access_token(self):
        """
        Refreshes the access token if it needs to be refreshed.
        """
        if not self.needs_refresh():
            return

        # Retrieves new tokens from Google servers.
        credentials = Credentials.from_authorized_user_info(info={
            'access_token': self.access_token,
            'refresh_token': self.refresh_token,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'token_uri': 'https://oauth2.googleapis.com/token'
        })
        credentials.refresh(google_requests.Request())

        # Updates the model.
        new_token = credentials.token
        self.access_token = new_token
        self.last_generated = datetime.now(timezone.utc)
        self.save()


class EmailVerificationToken(models.Model):
    """
    Model that stores the email verification token that has been sent. The token stored on the server is a
    hashed version of that which the user receives. The token should only be valid for 24 hours.

    Attributes:
      token (CharField): The token, stored as a SHA256 hash.
      user (ForeignKey[User]): The user associated with this token.
      created_at (DateTimeField): The time when the token was created.
    """
    token = models.CharField(max_length=64, primary_key=True)  # Token is stored as SHA256 hash.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create(cls, user):
        """
        Creates a new email verification token for a user, also sending the user the token through email.

        Arguments:
          user (User): The user for whom to create the token.

        Returns:
          EmailVerificationToken: The created token.
        """
        # Creates EmailVerificationToken model.
        random_string = str(uuid.uuid4())
        token_id = EmailVerificationToken.hash_token(random_string)
        token = cls(token=token_id, user=user)
        token.save()

        # Sends email to the user.
        send_mail("Hang Email Verification Code",
                  f"Welcome to Hang!\nClick on this link to verify your account: https://hang-coherentboi.vercel.app/verify?key={random_string}. This token will stay valid for 24 hours.",
                  settings.EMAIL_HOST_USER,
                  [token.user.email])

        return token

    def verify(self):
        """
        Verifies the user's email. If the user is already verified or the token is expired, raises a ValidationError.
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
        Hashes a token using SHA256.

        Arguments:
          token (str): The token to hash.

        Returns:
          str: The hashed token.
        """
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def is_expired(self):
        """
        Checks if the token is expired.

        Returns:
          bool: True if the token is expired, False otherwise.
        """
        return datetime.now(timezone.utc) - self.created_at > timedelta(days=1)


class FriendRequest(models.Model, RTWSSendMessageOnUpdate):
    """
    Model that represents a friend request between two users.

    Attributes:
      from_user (ForeignKey[User]): The user who sent the friend request.
      to_user (ForeignKey[User]): The user to whom the friend request was sent.
      declined (BooleanField): Whether the friend request was declined.
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
        Creates a new friend request from one user to another.

        Arguments:
          from_user (User): The user who is sending the friend request.
          to_user (User): The user to whom the friend request is being sent.

        Returns:
          FriendRequest: The created friend request.
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
        Accepts the friend request.
        """
        self.from_user.profile.add_friend(self.to_user)
        self.delete()

    def decline_friend_request(self):
        """
        Declines the friend request.
        """
        self.declined = True
        self.save()
