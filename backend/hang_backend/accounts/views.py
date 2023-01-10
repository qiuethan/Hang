from django.contrib.auth.models import User
from django.http import JsonResponse
from knox.models import AuthToken
from rest_framework import generics, permissions, status, views, exceptions
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from common.util.update_db import udbgenerics, udbmixins
from real_time_ws.utils import update_db_send_rtws_message
from .models import EmailAuthToken, FriendRequest
from .serializers import LoginSerializer, UserSerializer, RegisterSerializer, SendEmailSerializer, \
    VerifyEmailSerializer, FriendRequestReceivedSerializer, FriendRequestSentSerializer, UserDetailsSerializer


class RegisterView(views.APIView):
    """View to register a user."""

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return JsonResponse({
            "user": UserSerializer(user).data
        }, safe=False)


class LoginView(views.APIView):
    """View to log a user in."""

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })


class RetrieveUserViewID(generics.RetrieveAPIView):
    """View to retrieve a user by ID."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserDetailsSerializer
    queryset = User.objects.all()

    def get_object(self):
        return super(RetrieveUserViewID, self).get_object().userdetails


class RetrieveUserViewEmail(generics.RetrieveAPIView):
    """View to retrieve a user by ID."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserDetailsSerializer
    queryset = User.objects.all()
    lookup_field = "email"

    def get_object(self):
        return super(RetrieveUserViewEmail, self).get_object().userdetails


class RetrieveUserViewUsername(generics.RetrieveAPIView):
    """View to retrieve a user by ID."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserDetailsSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_object(self):
        return super(RetrieveUserViewUsername, self).get_object().userdetails


class RetrieveCurrentUserView(generics.RetrieveAPIView):
    """View that returns the currently logged-in user."""
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserDetailsSerializer

    def get_object(self):
        return self.request.user.userdetails


class SendVerificationEmailView(views.APIView):
    """View that send a verification email if the current user's account has not been verified."""

    def post(self, request):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailVerificationTokenView(views.APIView):
    """View that takes a user's verification token and verifies them."""

    def patch(self, request):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Updates user's profile.
        user = serializer.validated_data
        user.userdetails.is_verified = True
        user.userdetails.save()

        # Deletes EmailAuthToken.
        EmailAuthToken.objects.filter(user=user).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ListCreateSentFriendRequestView(udbgenerics.UpdateDBListCreateAPIView):
    """
    View that can list a user's friend requests and can create new friend requests.
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = FriendRequestSentSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["friend_request"]

    def get_queryset(self):
        return FriendRequest.objects.filter(from_user=self.request.user).all()

    def get_rtws_users(self, data):
        return {User.objects.get(id=data["from_user"]), User.objects.get(id=data["to_user"])}


class RetrieveDestroySentFriendRequestView(udbgenerics.UpdateDBRetrieveDestroyAPIView):
    """
    View that retrieves / deletes a friend request by ID.
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = FriendRequestSentSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["friend_request"]

    def get_object(self):
        query = FriendRequest.objects.filter(from_user=self.request.user, to_user=self.kwargs["user_id"])
        return get_object_or_404(query)

    def get_rtws_users(self, data):
        return {User.objects.get(id=data["from_user"]), User.objects.get(id=data["to_user"])}


class ListReceivedFriendRequestView(generics.ListAPIView):
    """
    View that lists all friend requests that have been received by the user.
    """
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = FriendRequestReceivedSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user).all()


class RetrieveAcceptDenyReceivedFriendRequestView(udbgenerics.UpdateDBRetrieveUpdateAPIView):
    """
    View that can retrieve, accept, or deny a friend request that a user a received.
    """
    permission_classes = {
        permissions.IsAuthenticated,
    }
    serializer_class = FriendRequestReceivedSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["friend_request", "friends"]  # TODO: seperate accept + deny, comment all new code

    def get_object(self):
        query = FriendRequest.objects.filter(from_user=self.kwargs["user_id"],
                                             to_user=self.request.user,
                                             declined=False)
        return get_object_or_404(query)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.from_user.userdetails.friends.add(instance.to_user)
        instance.to_user.userdetails.friends.add(instance.from_user)
        self.perform_update_db_actions(self.serializer_class(instance))
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_rtws_users(self, data):
        return {User.objects.get(id=data["from_user"]), User.objects.get(id=data["to_user"])}


class RemoveFriendsView(generics.GenericAPIView, udbmixins.UpdateDBGenericMixin):
    """
    View that allows a user to remove friends.
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["friends"]

    def get_queryset(self):
        return self.request.user.userdetails.friends.all()

    def delete(self, request, *args, **kwargs):
        self.perform_update_db_actions(self.get_serializer(self.get_object()), current_user=self.request.user)
        self.get_object().userdetails.friends.remove(self.request.user)
        self.request.user.userdetails.friends.remove(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_rtws_users(self, data):
        return {User.objects.get(id=data["id"])}

# TODO: add logic to friend block system
class ListFriendsView(generics.ListAPIView):
    """
    View that lists all a user's friends.
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.userdetails.friends.all()


class ListCreateBlockedUsersView(generics.ListAPIView, udbmixins.UpdateDBGenericMixin):
    """
    View that lists all the users that are blocked.
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["blocked_users"]

    def get_queryset(self):
        return self.request.user.userdetails.blocked_users.all()

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        blocked_user = serializer.validated_data
        if self.request.user == blocked_user:
            raise exceptions.ParseError("Cannot block yourself.")
        self.request.user.userdetails.blocked_users.add(blocked_user)
        self.perform_update_db_actions(current_user=self.request.user)
        return Response(status=HTTP_204_NO_CONTENT)

    def get_rtws_users(self, data):
        return {User.objects.get(id=data["id"])}


class RemoveBlockedUsersView(generics.GenericAPIView, udbmixins.UpdateDBGenericMixin):
    """
    View that allows a user to unblock another user.
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    serializer_class = UserSerializer
    update_db_actions = [update_db_send_rtws_message]
    rtws_update_actions = ["blocked_users"]

    def get_queryset(self):
        return self.request.user.userdetails.blocked_users.all()

    def delete(self, request, *args, **kwargs):
        self.request.user.userdetails.blocked_users.remove(self.get_object())
        self.perform_update_db_actions(current_user=self.request.user)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def get_rtws_users(self, data):
        return {User.objects.get(id=data["id"])}
