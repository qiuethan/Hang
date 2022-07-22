import random
import string

from django.core.mail import send_mail
from rest_framework import generics, permissions
from rest_framework.response import Response
from knox.models import AuthToken
from .serializers import LoginSerializer, UserSerializer, RegisterSerializer, SendEmailSerializer, VerifyEmailSerializer

# Register API
from hang_backend import settings
from .models import EmailAuthToken


class RegisterAPI(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# Login API
class LoginAPI(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)[1]
        })


# Get user API
class UserAPI(generics.RetrieveAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class SendEmail(generics.CreateAPIView):
    serializer_class = SendEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        def generate_random_string():
            return ''.join(
                [random.choice(string.ascii_letters) for _ in range(20)])

        ss = generate_random_string()
        while EmailAuthToken.objects.filter(id=ss).exists():
            ss = generate_random_string()

        token = EmailAuthToken(id=ss, user=serializer.validated_data)
        token.save()

        send_mail("""Verification Placeholder""",
                  f"""UWUUWUUWU\nwill be invalid after 24 hours\ntoken is localhost:3000/verify?key={token.id}\nchange the message in accounts/views.py""",
                  settings.EMAIL_HOST_USER,
                  [serializer.validated_data.email])
        return Response({'status': 'success'})


class VerifyEmail(generics.CreateAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        user.settings.is_verified = True
        user.settings.save()

        EmailAuthToken.objects.all().filter(user=user).delete()

        return Response({'status': 'success'})
