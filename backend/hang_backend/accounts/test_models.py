from django.test import TestCase
from django.contrib.auth.models import User
from .models import FriendRequest, EmailAuthToken, UserDetails


class ModelsTestCase(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.auth_token = EmailAuthToken.objects.create(id='1234567890abcdef', user=self.user1)
        self.friend_request = FriendRequest.objects.create(from_user=self.user1, to_user=self.user2)

    def test_user_details_model(self):
        self.assertEqual(self.user1.userdetails.user.username, 'user1')
        self.assertEqual(self.user1.userdetails.profile_picture, 'default profile pic change this later')
        self.assertFalse(self.user1.userdetails.is_verified)

    def test_email_auth_token_model(self):
        self.assertEqual(self.auth_token.user, self.user1)
        self.assertEqual(self.auth_token.id, '1234567890abcdef')

    def test_friend_request_model(self):
        self.assertEqual(self.friend_request.from_user, self.user1)
        self.assertEqual(self.friend_request.to_user, self.user2)
        self.assertFalse(self.friend_request.declined)
