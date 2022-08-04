from django.core.mail import send_mail
from django.http import JsonResponse
from knox.models import AuthToken
from rest_framework import generics, permissions, status, views, exceptions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from hang_backend import settings
from .models import EmailAuthToken, FriendRequest
from .serializers import LoginSerializer, UserSerializer, RegisterSerializer, SendEmailSerializer, \
    VerifyEmailSerializer, FriendRequestReceivedSerializer, FriendRequestSentSerializer, UserReaderSerializer


class RegisterView(views.APIView):
    """Method to register a user."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        }, safe=False)


class LoginView(views.APIView):
    """Method to log a user in."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })


class UserView(generics.RetrieveAPIView):
    """Method that returns the currently logged-in user."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class SendEmailView(views.APIView):
    """Method that send a verification email if the current user's account has not been verified."""

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.save()

        send_mail("Hang Email Verification Token",
                  f"Your email verification token is {token.id}. This token will stay valid for 24 hours.",
                  settings.EMAIL_HOST_USER,
                  [token.user.email])

        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailView(views.APIView):
    """Method that takes a user's verification token and verifies them."""

    def patch(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data
        user.userdetails.is_verified = True
        user.userdetails.save()

        EmailAuthToken.objects.filter(user=user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCreateSentFriendRequestView(generics.ListCreateAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = FriendRequestSentSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(from_user=self.request.user).all()


class RetrieveDestroySentFriendRequestView(generics.RetrieveDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = FriendRequestSentSerializer

    def get_object(self):
        query = FriendRequest.objects.filter(from_user=self.request.user, to_user=self.kwargs["user_id"])
        return get_object_or_404(query)


class ListReceivedFriendRequestView(generics.ListAPIView):
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = FriendRequestReceivedSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user).all()


class RetrieveUpdateDestroyReceivedFriendRequestView(generics.RetrieveUpdateAPIView):
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = FriendRequestReceivedSerializer

    def get_object(self):
        query = FriendRequest.objects.filter(from_user=self.kwargs["user_id"],
                                             to_user=self.request.user,
                                             declined=False)
        return get_object_or_404(query)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.from_user.userdetails.friends.add(instance.to_user)
        instance.to_user.userdetails.friends.add(instance.from_user)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RemoveFriendsView(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.userdetails.friends.all()

    def delete(self, request, *args, **kwargs):
        self.request.user.userdetails.friends.remove(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListFriendsView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.userdetails.friends.all()


class ListCreateBlockedUsersView(generics.ListAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.userdetails.blocked_users.all()

    def post(self, request):
        serializer = UserReaderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        blocked_user = serializer.validated_data
        if self.request.user == blocked_user:
            raise exceptions.ParseError("Cannot block yourself.")
        self.request.user.userdetails.blocked_users.add(blocked_user)
        return Response(status=HTTP_204_NO_CONTENT)


class RemoveBlockedUsersView(generics.GenericAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.userdetails.blocked_users.all()

    def delete(self, request, *args, **kwargs):
        self.request.user.userdetails.blocked_users.remove(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)
