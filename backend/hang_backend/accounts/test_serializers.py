import hashlib
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock

from django.core import mail
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import FriendRequest, EmailAuthToken
from .serializers import (
    UserSerializer,
    UserDetailsSerializer,
    FriendRequestReceivedSerializer,
    FriendRequestSentSerializer,
    RegisterSerializer,
    LoginSerializer,
    SendEmailSerializer, VerifyEmailSerializer,
)


class UserSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1", email="user1@example.com")

    def test_valid_user(self):
        serializer = UserSerializer(instance=self.user)
        expected_data = {
            "id": self.user.id,
            "username": "user1",
            "email": "user1@example.com",
        }
        self.assertEqual(serializer.data, expected_data)

    def test_user_does_not_exist(self):
        serializer = UserSerializer(data={"id": 1234})
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class UserDetailsSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username="user1", email="user1@example.com")
        self.user_details = self.user.userdetails

    def test_valid_user_details(self):
        serializer = UserDetailsSerializer(instance=self.user_details)
        expected_data = {
            "user": {
                "id": self.user.id,
                "username": "user1",
                "email": "user1@example.com",
            },
            "profile_picture": self.user_details.profile_picture,
            "is_verified": self.user_details.is_verified,
        }
        self.assertEqual(serializer.data, expected_data)


class FriendRequestReceivedSerializerTestCase(TestCase):
    def setUp(self):
        self.from_user = User.objects.create(username="user1", email="user1@example.com")
        self.to_user = User.objects.create(username="user2", email="user2@example.com")
        self.friend_request = self.from_user.sent_friend_requests.create(to_user=self.to_user)

    def test_valid_friend_request(self):
        serializer = FriendRequestReceivedSerializer(instance=self.friend_request)
        expected_data = {
            "from_user": self.from_user.id,
            "to_user": self.to_user.id,
            "declined": False,
        }
        self.assertEqual(serializer.data, expected_data)

    def test_update_friend_request(self):
        serializer = FriendRequestReceivedSerializer(instance=self.friend_request, data={"declined": True},
                                                     partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.friend_request.refresh_from_db()
        self.assertTrue(self.friend_request.declined)


class FriendRequestSentSerializerTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='test1', email='test1@example.com', password='testpassword')
        self.user2 = User.objects.create_user(username='test2', email='test2@example.com', password='testpassword')

    def test_create_friend_request(self):
        data = {'to_user': self.user2.pk}
        serializer = FriendRequestSentSerializer(data=data, context={'request': MagicMock(user=self.user1)})
        self.assertTrue(serializer.is_valid())

        with patch('accounts.serializers.FriendRequest.objects.filter') as mock_filter:
            mock_filter.return_value.exists.return_value = False
            request = serializer.save()

        self.assertEqual(request.from_user, self.user1)
        self.assertEqual(request.to_user, self.user2)

    def test_create_friend_request_to_self(self):
        data = {'to_user': self.user1.pk}
        serializer = FriendRequestSentSerializer(data=data, context={'request': MagicMock(user=self.user1)})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'non_field_errors': ['Cannot send a friend request to yourself.']})

    def test_create_friend_request_already_friends(self):
        self.user1.userdetails.friends.add(self.user2)
        data = {'to_user': self.user2.pk}
        serializer = FriendRequestSentSerializer(data=data, context={'request': MagicMock(user=self.user1)})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'non_field_errors': ['User is already a friend.']})

    def test_create_friend_request_already_requested(self):
        FriendRequest.objects.create(from_user=self.user2, to_user=self.user1)
        data = {'to_user': self.user2.pk}
        serializer = FriendRequestSentSerializer(data=data, context={'request': MagicMock(user=self.user1)})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'non_field_errors': ['This user has already sent you a friend request.']})

    def test_create_friend_request_request_exists(self):
        FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)
        data = {'to_user': self.user2.pk}
        serializer = FriendRequestSentSerializer(data=data, context={'request': MagicMock(user=self.user1)})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors, {'non_field_errors': ['Friend request already exists.']})


class TestRegisterSerializer(TestCase):
    def test_create(self):
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        }
        serializer = RegisterSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        self.assertEqual(user.username, data["username"])
        self.assertEqual(user.email, data["email"])
        self.assertTrue(user.check_password(data["password"]))


class TestLoginSerializer(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123"
        )
        self.user.userdetails.is_verified = True
        self.user.userdetails.save()

    def test_validate_success(self):
        data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        self.assertEqual(user, self.user)

    def test_validate_incorrect_credentials(self):
        data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        serializer = LoginSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_validate_user_not_verified(self):
        data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        self.user.userdetails.is_verified = False
        self.user.userdetails.save()
        serializer = LoginSerializer(data=data)
        with self.assertRaises(serializers.ValidationError):
            serializer.is_valid(raise_exception=True)


class SendEmailSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')

    def test_validate_with_incorrect_credentials(self):
        data = {'email': 'test@example.com', 'password': 'incorrectpassword'}
        serializer = SendEmailSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_validate_with_already_verified_user(self):
        self.user.userdetails.is_verified = True
        self.user.userdetails.save()
        data = {'email': 'test@example.com', 'password': 'testpassword'}
        serializer = SendEmailSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_create_and_send_mail(self):
        data = {'email': 'test@example.com', 'password': 'testpassword'}
        serializer = SendEmailSerializer(data=data)
        serializer.is_valid()
        serializer.save()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Hang Email Verification Token')
        self.assertIn('Your email verification token is', mail.outbox[0].body)


class VerifyEmailSerializerTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpassword')
        self.ss = "abcdefghijklmnopqrst"
        self.token = EmailAuthToken.objects.create(id=hashlib.sha256(self.ss.encode("utf-8")).hexdigest(),
                                                   user=self.user)

    def test_validate_with_nonexistent_token(self):
        data = {'token': 'nonexistenttoken'}
        serializer = VerifyEmailSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_validate_with_already_verified_user(self):
        self.user.userdetails.is_verified = True
        self.user.userdetails.save()
        data = {'token': self.ss}
        serializer = VerifyEmailSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_validate_with_expired_token(self):
        self.token.created_at = datetime.now(timezone.utc) - timedelta(days=2)
        self.token.save()
        data = {'token': self.ss}
        serializer = VerifyEmailSerializer(data=data)
        self.assertFalse(serializer.is_valid())

    def test_validate_successful(self):
        data = {'token': self.ss}
        serializer = VerifyEmailSerializer(data=data)
        serializer.is_valid()
        self.assertEqual(serializer.validated_data, self.user)
