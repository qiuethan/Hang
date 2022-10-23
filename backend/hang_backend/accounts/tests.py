import json
from datetime import datetime, timedelta, timezone

from knox import crypto
from knox.models import AuthToken
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from rest_framework.test import APIClient
from freezegun import freeze_time

from accounts.models import UserDetails, EmailAuthToken, FriendRequest


class RegisterTest(TestCase):
    def setUp(self):
        User.objects.create_user("test_user_1", "test_user_1@gmail.com", "test_user_1_password")
        self.client = APIClient()

    def testRegisterUserValid(self):
        response = self.client.post("/v1/accounts/register",
                                    {"username": "test_user_2", "email": "test_user_2@gmail.com",
                                     "password": "test_user_2_password"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"user": {"id": 2, "username": "test_user_2", "email": "test_user_2@gmail.com"}}')

    def testRegisterUserSameUsername(self):
        response = self.client.post("/v1/accounts/register",
                                    {"username": "test_user_1", "email": "test_user_2@gmail.com",
                                     "password": "test_user_1_password"})
        self.assertEqual(response.status_code, 400)

    def testRegisterUserSameEmail(self):
        response = self.client.post("/v1/accounts/register",
                                    {"username": "test_user_2", "email": "test_user_1@gmail.com",
                                     "password": "test_user_1_password"})
        self.assertEqual(response.status_code, 400)

    def testRegisterUserMaxLengthUsername(self):
        response = self.client.post("/v1/accounts/register", {
            "username": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "email": "test_user_2@gmail.com",
            "password": "test_user_2_password"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"user": {"id": 2, "username": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "email": "test_user_2@gmail.com"}}')

    def testRegisterUserTooLongUsername(self):
        response = self.client.post("/v1/accounts/register", {
            "username": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "email": "test_user_2@gmail.com",
            "password": "test_user_2_password"})
        self.assertEqual(response.status_code, 400)

    def testRegisterUserMalformedEmail(self):
        response = self.client.post("/v1/accounts/register",
                                    {"username": "test_user_2", "email": "aaaaaaaaaaa",
                                     "password": "test_user_2_password"})
        self.assertEqual(response.status_code, 400)


class LoginTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user("test_user_1", "test_user_1@gmail.com", "test_user_1_password")
        self.user_details1 = UserDetails.objects.create(is_verified=True)
        self.user_details1.user = self.user1
        self.client = APIClient()

    def testLogin(self):
        for i in range(5):
            response = self.client.post("/v1/accounts/login",
                                        {"email": "test_user_1@gmail.com", "password": "test_user_1_password"})
            self.assertEqual(response.status_code, 200)
            content_dict = json.loads(response.content)
            self.assertEqual(content_dict["user"]["id"], 1)
            self.assertEqual(content_dict["user"]["username"], "test_user_1")
            self.assertEqual(content_dict["user"]["email"], "test_user_1@gmail.com")
            self.assertTrue("token" in content_dict)
            self.assertEqual(AuthToken.objects.count(), i + 1)
            self.assertTrue(AuthToken.objects.filter(digest=crypto.hash_token(content_dict["token"])).exists)

    def testLoginInvalidEmail(self):
        response = self.client.post("/v1/accounts/login",
                                    {"email": "test_user@gmail.com", "password": "test_user_1_password"})
        self.assertEqual(response.status_code, 400)

    def testLoginInvalidPassword(self):
        response = self.client.post("/v1/accounts/login",
                                    {"email": "test_user_1@gmail.com", "password": "test_user_password"})
        self.assertEqual(response.status_code, 400)


class LogoutTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user("test_user_1", "test_user_1@gmail.com", "test_user_1_password")
        self.user_details1 = UserDetails.objects.create(is_verified=True)
        self.user_details1.user = self.user1
        self.client = APIClient()
        response = self.client.post("/v1/accounts/login",
                                    {"email": "test_user_1@gmail.com", "password": "test_user_1_password"})
        self.token = json.loads(response.content)["token"]

    def testLogout(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post("/v1/accounts/logout")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(AuthToken.objects.count(), 0)

    def testLogoutNoToken(self):
        response = self.client.post("/v1/accounts/logout")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(AuthToken.objects.count(), 1)

    def testLogoutInvalidToken(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token aaaaaaaaaaaaaaaaaaaa")
        response = self.client.post("/v1/accounts/logout")
        self.assertEqual(response.status_code, 401)
        self.assertEqual(AuthToken.objects.count(), 1)


class SendEmailVerificationTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user("test_user_1", "test_user_1@gmail.com", "test_user_1_password")
        self.user_details1 = UserDetails.objects.create()
        self.user_details1.user = self.user1
        self.client = APIClient()

    def testSendEmailVerificationBasic(self):
        response = self.client.post("/v1/accounts/send_email",
                                    {"email": "test_user_1@gmail.com", "password": "test_user_1_password"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Hang Email Verification Token")
        self.assertEqual(len(mail.outbox[0].body), 95)
        self.assertEqual(mail.outbox[0].body[0:33], "Your email verification token is ")
        self.assertEqual(mail.outbox[0].body[53:], ". This token will stay valid for 24 hours.")

    def testSendEmailVerificationAlreadyVerified(self):
        self.user_details1.is_verified = True
        self.user_details1.save()
        response = self.client.post("/v1/accounts/send_email",
                                    {"email": "test_user_1@gmail.com", "password": "test_user_1_password"})
        self.assertEqual(response.status_code, 400)

    def testSendMultipleEmailVerification(self):
        response = self.client.post("/v1/accounts/send_email",
                                    {"email": "test_user_1@gmail.com", "password": "test_user_1_password"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Hang Email Verification Token")
        self.assertEqual(len(mail.outbox[0].body), 95)
        self.assertEqual(mail.outbox[0].body[0:33], "Your email verification token is ")
        self.assertEqual(mail.outbox[0].body[53:], ". This token will stay valid for 24 hours.")
        token1 = mail.outbox[0].body[33:53]

        response = self.client.post("/v1/accounts/send_email",
                                    {"email": "test_user_1@gmail.com", "password": "test_user_1_password"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Hang Email Verification Token")
        self.assertEqual(len(mail.outbox[1].body), 95)
        self.assertEqual(mail.outbox[1].body[0:33], "Your email verification token is ")
        self.assertEqual(mail.outbox[1].body[53:], ". This token will stay valid for 24 hours.")
        token2 = mail.outbox[1].body[33:53]

        self.assertNotEqual(token1, token2)


class VerifyEmailVerificationTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user("test_user_1", "test_user_1@gmail.com", "test_user_1_password")
        self.user_details1 = UserDetails.objects.create()
        self.user_details1.user = self.user1

        self.client = APIClient()

        self.client.post("/v1/accounts/send_email",
                         {"email": "test_user_1@gmail.com", "password": "test_user_1_password"})
        self.client.post("/v1/accounts/send_email",
                         {"email": "test_user_1@gmail.com", "password": "test_user_1_password"})
        self.token1 = mail.outbox[0].body[33:53]
        self.token2 = mail.outbox[1].body[33:53]

    def testVerifyEmailVerificationToken(self):
        response = self.client.patch("/v1/accounts/verify_email", {"token": self.token1})
        self.assertEqual(response.status_code, 204)
        self.user_details1.refresh_from_db()
        self.assertTrue(self.user_details1.is_verified)
        self.assertEqual(EmailAuthToken.objects.count(), 0)

    def testVerifyMultipleEmailVerificationToken(self):
        response = self.client.patch("/v1/accounts/verify_email", {"token": self.token1})
        self.assertEqual(response.status_code, 204)
        self.user_details1.refresh_from_db()
        self.assertTrue(self.user_details1.is_verified)

        response = self.client.patch("/v1/accounts/verify_email", {"token": self.token1})
        self.assertEqual(response.status_code, 400)

        response = self.client.patch("/v1/accounts/verify_email", {"token": self.token2})
        self.assertEqual(response.status_code, 400)

    def testVerifyInvalidEmailVerificationToken(self):
        response = self.client.patch("/v1/accounts/verify_email", {"token": "aaaaaaaaaaaaaaaaaaaa"})
        self.assertEqual(response.status_code, 400)
        self.user_details1.refresh_from_db()
        self.assertFalse(self.user_details1.is_verified)

    def testVerifyEmailAfter23Hours(self):
        with freeze_time(datetime.now()) as frozen_datetime:
            frozen_datetime.move_to(datetime.now() + timedelta(hours=23))
            response = self.client.patch("/v1/accounts/verify_email", {"token": self.token1})
            self.assertEqual(response.status_code, 204)
            self.user_details1.refresh_from_db()
            self.assertTrue(self.user_details1.is_verified)

    def testVerifyEmailAfter25Hours(self):
        with freeze_time(datetime.now(timezone.utc)) as frozen_datetime:
            frozen_datetime.move_to(datetime.now() + timedelta(hours=25))
            response = self.client.patch("/v1/accounts/verify_email", {"token": self.token1})
            self.assertEqual(response.status_code, 400)


class SentFriendRequestTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test_user_1", email="test_user_1@gmail.com",
                                              password="test_user_1_password")
        self.user1.userdetails = UserDetails.objects.create(is_verified=True)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = User.objects.create_user(username="test_user_2", email="test_user_2@gmail.com",
                                              password="test_user_2_password")
        self.user2.userdetails = UserDetails.objects.create(is_verified=True)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def testSendFriendRequest(self):
        response = self.client.post("/v1/accounts/sent_friend_request", {"to_user": {"id": 2}},
                                    format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.content,
                         b'{"from_user":{"id":1,"username":"test_user_1","email":"test_user_1@gmail.com"},"to_user":{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"}}')

        self.assertEqual(FriendRequest.objects.count(), 1)
        friend_request = FriendRequest.objects.get()
        self.assertEqual(friend_request.from_user.id, 1)
        self.assertEqual(friend_request.to_user.id, 2)
        self.assertEqual(friend_request.declined, False)

    def testMultipleSendFriendRequest(self):
        FriendRequest.objects.create(from_user=User.objects.get(id=1), to_user=User.objects.get(id=2), declined=False)
        response = self.client.post("/v1/accounts/sent_friend_request", {"to_user": {"id": 2}},
                                    format="json")
        self.assertEqual(response.status_code, 400)

    def testSendFriendRequestToSelf(self):
        response = self.client.post("/v1/accounts/sent_friend_request", {"to_user": {"id": 1}},
                                    format="json")
        self.assertEqual(response.status_code, 400)

    def testLoadFriendRequest(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=1),
                                                           to_user=User.objects.get(id=2), declined=False)
        response = self.client.get("/v1/accounts/sent_friend_request")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'[{"from_user":{"id":1,"username":"test_user_1","email":"test_user_1@gmail.com"},"to_user":{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"}}]'
                         )

        self.friend_request.declined = True
        self.friend_request.save()

        response = self.client.get("/v1/accounts/sent_friend_request")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'[{"from_user":{"id":1,"username":"test_user_1","email":"test_user_1@gmail.com"},"to_user":{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"}}]'
                         )

    def testRetrieveFriendRequest(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=1),
                                                           to_user=User.objects.get(id=2), declined=False)
        response = self.client.get("/v1/accounts/sent_friend_request/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"from_user":{"id":1,"username":"test_user_1","email":"test_user_1@gmail.com"},"to_user":{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"}}')

    def testRetrieveNonExistentFriendRequest(self):
        response = self.client.get("/v1/accounts/sent_friend_request/2")
        self.assertEqual(response.status_code, 404)

    def testDeleteFriendRequest(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=1),
                                                           to_user=User.objects.get(id=2), declined=False)
        response = self.client.delete("/v1/accounts/sent_friend_request/2")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(FriendRequest.objects.count(), 0)

    def testDeleteNonExistentFriendRequest(self):
        response = self.client.delete("/v1/accounts/sent_friend_request/2")
        self.assertEqual(response.status_code, 404)


class ReceivedFriendRequestTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test_user_1", email="test_user_1@gmail.com",
                                              password="test_user_1_password")
        self.user1.userdetails = UserDetails.objects.create(is_verified=True)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = User.objects.create_user(username="test_user_2", email="test_user_2@gmail.com",
                                              password="test_user_2_password")
        self.user2.userdetails = UserDetails.objects.create(is_verified=True)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def testLoadFriendRequest(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=2),
                                                           to_user=User.objects.get(id=1), declined=False)
        response = self.client.get("/v1/accounts/received_friend_request")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'[{"from_user":{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"},"to_user":{"id":1,"username":"test_user_1","email":"test_user_1@gmail.com"},"declined":false}]'
                         )

        self.friend_request.declined = True
        self.friend_request.save()

        response = self.client.get("/v1/accounts/received_friend_request")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'[{"from_user":{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"},"to_user":{"id":1,"username":"test_user_1","email":"test_user_1@gmail.com"},"declined":true}]')

    def testRetrieveFriendRequest(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=2),
                                                           to_user=User.objects.get(id=1), declined=False)
        response = self.client.get("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"from_user":{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"},"to_user":{"id":1,"username":"test_user_1","email":"test_user_1@gmail.com"},"declined":false}')

    def testRetrieveNonExistentFriendRequest(self):
        response = self.client.get("/v1/accounts/sent_friend_request/2")
        self.assertEqual(response.status_code, 404)

    def testAcceptFriendRequest(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=2),
                                                           to_user=User.objects.get(id=1), declined=False)
        response = self.client.delete("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user1.userdetails.friends.count(), 1)

    def testAcceptNonExistentFriendRequest(self):
        response = self.client.delete("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user1.userdetails.friends.count(), 0)

    def testDeclineFriendRequest(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=2),
                                                           to_user=User.objects.get(id=1), declined=False)
        response = self.client.patch("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 200)
        self.friend_request.refresh_from_db()
        self.assertEqual(self.friend_request.declined, True)

    def testDeclineNonExistentFriendRequest(self):
        response = self.client.patch("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 404)


class FriendsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test_user_1", email="test_user_1@gmail.com",
                                              password="test_user_1_password")
        self.user1.userdetails = UserDetails.objects.create(is_verified=True)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = User.objects.create_user(username="test_user_2", email="test_user_2@gmail.com",
                                              password="test_user_2_password")
        self.user2.userdetails = UserDetails.objects.create(is_verified=True)

        self.user1.userdetails.friends.add(self.user2)
        self.user2.userdetails.friends.add(self.user1)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def testListFriends(self):
        response = self.client.get("/v1/accounts/friends")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"}]')

    def testRemoveFriends(self):
        response = self.client.delete("/v1/accounts/friends/2")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user1.userdetails.friends.count(), 0)
        self.assertEqual(self.user2.userdetails.friends.count(), 0)


class BlockedUsersTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username="test_user_1", email="test_user_1@gmail.com",
                                              password="test_user_1_password")
        self.user1.userdetails = UserDetails.objects.create(is_verified=True)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = User.objects.create_user(username="test_user_2", email="test_user_2@gmail.com",
                                              password="test_user_2_password")
        self.user2.userdetails = UserDetails.objects.create(is_verified=True)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def testListBlockedUsers(self):
        self.user1.userdetails.blocked_users.add(self.user2)
        response = self.client.get("/v1/accounts/blocked_users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'[{"id":2,"username":"test_user_2","email":"test_user_2@gmail.com"}]')

    def testAddBlockedUsers(self):
        response = self.client.post("/v1/accounts/blocked_users", {"id": 2})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user1.userdetails.blocked_users.count(), 1)

    def testRemoveBlockedUsers(self):
        self.user1.userdetails.blocked_users.add(self.user2)
        response = self.client.delete("/v1/accounts/blocked_users/2")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user1.userdetails.blocked_users.count(), 0)

# TODO: Discuss with Ethan on Retrieving user by ID