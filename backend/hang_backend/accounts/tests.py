import json

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from knox.models import AuthToken
from rest_framework.test import APIClient


class AuthenticationTest(TestCase):
    def test_authentication(self):
        c = APIClient()

        # Creates two users
        response = c.post("/v1/accounts/register",
                          {"username": "testuser", "email": "testuser@gmail.com", "password": "testpassword"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"user": {"id": 1, "username": "testuser", "email": "testuser@gmail.com"}}')

        response = c.post("/v1/accounts/register",
                          {"username": "testuser1", "email": "testuser1@gmail.com", "password": "testpassword"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content,
                         b'{"user": {"id": 2, "username": "testuser1", "email": "testuser1@gmail.com"}}')

        # Verifies that it's impossible to create two users with the same username or email.
        response = c.post("/v1/accounts/register",
                          {"username": "testuser1", "email": "testuser@gmail.com", "password": "testpassword"})
        self.assertEqual(response.status_code, 400)

        response = c.post("/v1/accounts/register",
                          {"username": "testuser", "email": "testuser1@gmail.com", "password": "testpassword"})
        self.assertEqual(response.status_code, 400)

        # Verifies email verification.
        response = c.post("/v1/accounts/send_email", {"email": "testuser@gmail.com", "password": "testpassword"})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(len(mail.outbox), 1)

        token = mail.outbox[0].body.split()[5][:-1]
        response = c.patch("/v1/accounts/verify_email", {"token": token})
        self.assertEqual(response.status_code, 204)
        self.assertTrue(User.objects.filter(username="testuser").get().userdetails.is_verified)

        # Verifies login and logout.

        response = c.post("/v1/accounts/login", {"email": "testuser@gmail.com", "password": "testpassword"})
        res_dict = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue({"user", "token"} <= res_dict.keys() and {"username", "email", "id"} <= res_dict["user"].keys())
        self.assertEqual(AuthToken.objects.count(), 1)
        self.assertEqual(AuthToken.objects.get().user.username, "testuser")

        c.credentials(HTTP_AUTHORIZATION="Token " + res_dict["token"])
        response = c.post("/v1/accounts/logout", {})
        self.assertEqual(response.status_code, 204)
        self.assertEqual(AuthToken.objects.count(), 0)
