import json
import re
from datetime import datetime, timedelta, timezone

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from freezegun import freeze_time
from knox import crypto
from knox.models import AuthToken
from rest_framework.test import APIClient

from accounts.models import UserDetails, FriendRequest


def build_user(username, email, password, is_verified=True):
    user = User.objects.create_user(username, email, password)
    user.userdetails.is_verified = is_verified
    user.userdetails.save()
    return user


def build_numbered_test_user(_id, is_verified=True):
    user = User.objects.create_user(f"test_user_{_id}", f"test_user_{_id}@gmail.com", f"test_user_{_id}_password")
    user.userdetails.is_verified = is_verified
    user.userdetails.save()
    return user


def dict_user(_id, username, email):
    return {
        "id": _id,
        "username": username,
        "email": email
    }


def dict_numbered_test_user(_id):
    return {
        "id": _id,
        "username": f"test_user_{_id}",
        "email": f"test_user_{_id}@gmail.com"
    }


def dict_sent_friend_request(id1, id2):
    return {
        "from_user": id1,
        "to_user": id2
    }


def dict_received_friend_request(id1, id2, declined):
    return {
        "from_user": id1,
        "to_user": id2,
        "declined": declined
    }


class RegisterTest(TestCase):
    def setUp(self):
        build_numbered_test_user(1, is_verified=False)
        self.client = APIClient()

    def test_register_user_valid(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "test_user_2",
            "email": "test_user_2@gmail.com",
            "password": "test_user_2_password"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"user": dict_numbered_test_user(2)})

    def test_register_user_same_username(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "test_user_1",
            "email": "test_user_2@gmail.com",
            "password": "test_user_1_password"
        })
        self.assertEqual(response.status_code, 400)

    def test_register_user_same_email(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "test_user_2",
            "email": "test_user_1@gmail.com",
            "password": "test_user_1_password"
        })
        self.assertEqual(response.status_code, 400)

    def test_register_user_max_length_username(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "email": "test_user_2@gmail.com",
            "password": "test_user_2_password"
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {
            "user": dict_user(2,
                              "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                              "test_user_2@gmail.com")
        })

    def test_register_user_too_long_username(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "email": "test_user_2@gmail.com",
            "password": "test_user_2_password"
        })
        self.assertEqual(response.status_code, 400)

    def test_register_user_malformed_email(self):
        response = self.client.post(reverse("accounts:register"), {
            "username": "test_user_2",
            "email": "aaaaaaaaaaa",
            "password": "test_user_2_password"
        })
        self.assertEqual(response.status_code, 400)


class LoginTest(TestCase):
    def setUp(self):
        self.user1 = build_numbered_test_user(1)
        self.client = APIClient()

    def test_login(self):
        for i in range(2):
            response = self.client.post(reverse("accounts:login"), {
                "email": "test_user_1@gmail.com",
                "password": "test_user_1_password"
            })
            self.assertEqual(response.status_code, 200)
            content_dict = json.loads(response.content)
            self.assertEqual(content_dict["user"], dict_numbered_test_user(1))
            self.assertEqual(AuthToken.objects.count(), i + 1)
            self.assertTrue(AuthToken.objects.filter(digest=crypto.hash_token(content_dict["token"])).exists)

    def test_login_invalid_email(self):
        response = self.client.post(reverse("accounts:login"), {
            "email": "test_user@gmail.com",
            "password": "test_user_1_password"
        })
        self.assertEqual(response.status_code, 400)

    def test_login_invalid_password(self):
        response = self.client.post(reverse("accounts:login"), {
            "email": "test_user_1@gmail.com",
            "password": "test_user_password"
        })
        self.assertEqual(response.status_code, 400)


class LogoutTest(TestCase):
    def setUp(self):
        self.user1 = build_numbered_test_user(1)
        self.client = APIClient()
        response = self.client.post(reverse("accounts:login"), {
            "email": "test_user_1@gmail.com",
            "password": "test_user_1_password"
        })
        self.token = json.loads(response.content)["token"]

    def test_logout(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token)
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(AuthToken.objects.count(), 0)

    def test_logout_no_token(self):
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(AuthToken.objects.count(), 1)

    def test_logout_invalid_token(self):
        self.client.credentials(HTTP_AUTHORIZATION="Token aaaaaaaaaaaaaaaaaaaa")
        response = self.client.post(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 401)
        self.assertEqual(AuthToken.objects.count(), 1)


class SendEmailVerificationTest(TestCase):
    def setUp(self):
        self.user1 = build_numbered_test_user(1, is_verified=False)
        self.client = APIClient()

    def test_send_email_verification(self):
        for i in range(2):
            response = self.client.post(reverse("accounts:send_verification_email"), {
                "email": "test_user_1@gmail.com",
                "password": "test_user_1_password"
            })
            self.assertEqual(response.status_code, 204)
            self.assertEqual(len(mail.outbox), i + 1)
            self.assertEqual(mail.outbox[i].subject, "Hang Email Verification Token")
            self.assertNotEqual(
                re.search(r"^Your email verification token is .{20}\. This token will stay valid for 24 hours\.$",
                          mail.outbox[i].body), None)

    def test_send_email_verification_already_verified(self):
        self.user1.userdetails.is_verified = True
        self.user1.userdetails.save()
        response = self.client.post(reverse("accounts:send_verification_email"), {
            "email": "test_user_1@gmail.com",
            "password": "test_user_1_password"
        })
        self.assertEqual(response.status_code, 400)


class VerifyEmailVerificationTest(TestCase):

    def setUp(self):
        self.user1 = build_numbered_test_user(1, is_verified=False)

        self.client = APIClient()

        self.client.post(reverse("accounts:send_verification_email"), {
            "email": "test_user_1@gmail.com",
            "password": "test_user_1_password"
        })
        self.client.post(reverse("accounts:send_verification_email"), {
            "email": "test_user_1@gmail.com",
            "password": "test_user_1_password"
        })
        self.token1 = mail.outbox[0].body[33:53]
        self.token2 = mail.outbox[1].body[33:53]

    def test_verify_email_verification_token(self):
        response = self.client.patch(reverse("accounts:verify_email_token"), {"token": self.token1})
        self.assertEqual(response.status_code, 204)
        self.user1.userdetails.refresh_from_db()
        self.assertTrue(self.user1.userdetails.is_verified)

        response = self.client.patch(reverse("accounts:verify_email_token"), {"token": self.token1})
        self.assertEqual(response.status_code, 400)

        response = self.client.patch(reverse("accounts:verify_email_token"), {"token": self.token2})
        self.assertEqual(response.status_code, 400)

    def test_verify_invalid_email_verification_token(self):
        response = self.client.patch(reverse("accounts:verify_email_token"), {"token": "aaaaaaaaaaaaaaaaaaaa"})
        self.assertEqual(response.status_code, 400)
        self.user1.userdetails.refresh_from_db()
        self.assertFalse(self.user1.userdetails.is_verified)

    def test_verify_email_after_23_hours(self):
        with freeze_time(datetime.now()) as frozen_datetime:
            frozen_datetime.move_to(datetime.now() + timedelta(hours=23))
            response = self.client.patch(reverse("accounts:verify_email_token"), {"token": self.token1})
            self.assertEqual(response.status_code, 204)
            self.user1.userdetails.refresh_from_db()
            self.assertTrue(self.user1.userdetails.is_verified)

    def test_verify_email_after_25_hours(self):
        with freeze_time(datetime.now(timezone.utc)) as frozen_datetime:
            frozen_datetime.move_to(datetime.now() + timedelta(hours=25))
            response = self.client.patch(reverse("accounts:verify_email_token"), {"token": self.token1})
            self.assertEqual(response.status_code, 400)


class SentFriendRequestTest(TestCase):
    def setUp(self):
        self.user1 = build_numbered_test_user(1)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = build_numbered_test_user(2)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def test_send_friend_request(self):
        response = self.client.post(reverse("accounts:list_create_sent_friend_request"), {"to_user": 2}, format="json")
        self.assertEqual(response.status_code, 201)
        content_dict = json.loads(response.content)
        self.assertEqual(content_dict, dict_sent_friend_request(1, 2))

        self.assertEqual(FriendRequest.objects.count(), 1)
        self.assertEqual(FriendRequest.objects.get().declined, False)

    def test_multiple_send_friend_request(self):
        FriendRequest.objects.create(from_user=User.objects.get(id=1), to_user=User.objects.get(id=2), declined=False)
        response = self.client.post(reverse("accounts:list_create_sent_friend_request"), {"to_user": 2}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_send_friend_request_to_self(self):
        response = self.client.post(reverse("accounts:list_create_sent_friend_request"), {"to_user": 1}, format="json")
        self.assertEqual(response.status_code, 400)

    def test_load_friend_request(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=1),
                                                           to_user=User.objects.get(id=2), declined=False)
        response = self.client.get(reverse("accounts:list_create_sent_friend_request"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [dict_sent_friend_request(1, 2)])

        self.friend_request.declined = True
        self.friend_request.save()

        response = self.client.get(reverse("accounts:list_create_sent_friend_request"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [dict_sent_friend_request(1, 2)])

    def test_retrieve_friend_request(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=1),
                                                           to_user=User.objects.get(id=2), declined=False)
        response = self.client.get(reverse("accounts:retrieve_destroy_sent_friend_request", args=(2,)))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), dict_sent_friend_request(1, 2))

    def test_retrieve_non_existent_friend_request(self):
        response = self.client.get(reverse("accounts:retrieve_destroy_sent_friend_request", args=(2,)))
        self.assertEqual(response.status_code, 404)

    def test_delete_friend_request(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=1),
                                                           to_user=User.objects.get(id=2), declined=False)
        response = self.client.delete(reverse("accounts:retrieve_destroy_sent_friend_request", args=(2,)))
        self.assertEqual(response.status_code, 204)
        self.assertEqual(FriendRequest.objects.count(), 0)

    def test_delete_non_existent_friend_request(self):
        response = self.client.delete(reverse("accounts:retrieve_destroy_sent_friend_request", args=(2,)))
        self.assertEqual(response.status_code, 404)


class ReceivedFriendRequestTest(TestCase):
    def setUp(self):
        self.user1 = build_numbered_test_user(1)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = build_numbered_test_user(2)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def test_load_friend_request(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=2),
                                                           to_user=User.objects.get(id=1), declined=False)
        response = self.client.get("/v1/accounts/received_friend_request")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [dict_received_friend_request(2, 1, False)])

        self.friend_request.declined = True
        self.friend_request.save()

        response = self.client.get("/v1/accounts/received_friend_request")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [dict_received_friend_request(2, 1, True)])

    def test_retrieve_friend_request(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=2),
                                                           to_user=User.objects.get(id=1), declined=False)
        response = self.client.get("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), dict_received_friend_request(2, 1, False))

    def test_retrieve_non_existent_friend_request(self):
        response = self.client.get(reverse("accounts:retrieve_destroy_sent_friend_request", args=(2,)))
        self.assertEqual(response.status_code, 404)

    def test_accept_friend_request(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=2),
                                                           to_user=User.objects.get(id=1), declined=False)
        response = self.client.delete("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user1.userdetails.friends.count(), 1)

    def test_accept_non_existent_friend_request(self):
        response = self.client.delete("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.user1.userdetails.friends.count(), 0)

    def test_decline_friend_request(self):
        self.friend_request = FriendRequest.objects.create(from_user=User.objects.get(id=2),
                                                           to_user=User.objects.get(id=1), declined=False)
        response = self.client.patch("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 200)
        self.friend_request.refresh_from_db()
        self.assertEqual(self.friend_request.declined, True)

    def test_decline_non_existent_friend_request(self):
        response = self.client.patch("/v1/accounts/received_friend_request/2")
        self.assertEqual(response.status_code, 404)


class FriendsTest(TestCase):
    def setUp(self):
        self.user1 = build_numbered_test_user(1)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = build_numbered_test_user(2)

        self.user1.userdetails.friends.add(self.user2)
        self.user2.userdetails.friends.add(self.user1)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def test_list_friends(self):
        response = self.client.get("/v1/accounts/friends")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [2])

    def test_remove_friends(self):
        response = self.client.delete("/v1/accounts/friends/2")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user1.userdetails.friends.count(), 0)
        self.assertEqual(self.user2.userdetails.friends.count(), 0)


class BlockedUsersTest(TestCase):
    def setUp(self):
        self.user1 = build_numbered_test_user(1)
        self.token1 = AuthToken.objects.create(self.user1)[1]

        self.user2 = build_numbered_test_user(2)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token1)

    def test_list_blocked_users(self):
        self.user1.userdetails.blocked_users.add(self.user2)
        response = self.client.get("/v1/accounts/blocked_users")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), [2])

    def test_add_blocked_users(self):
        response = self.client.post("/v1/accounts/blocked_users", {"id": 2})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user1.userdetails.blocked_users.count(), 1)

    def test_remove_blocked_users(self):
        self.user1.userdetails.blocked_users.add(self.user2)
        response = self.client.delete("/v1/accounts/blocked_users/2")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(self.user1.userdetails.blocked_users.count(), 0)
