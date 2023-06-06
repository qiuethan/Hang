"""
ICS4U
Paul Chen
This module contains views for handling user authentication, profile management, friend requests, and user blocking in a Django application.
"""

from django.contrib.auth.models import User
from django.http import JsonResponse
from knox.models import AuthToken
from rest_framework import generics, permissions, status, views, viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from .models import EmailAuthenticationToken, FriendRequest, Profile, GoogleAuthenticationToken
from .serializers import (
    LoginSerializer,
    UserSerializer,
    RegisterSerializer,
    EmailAuthenticationTokenSerializer,
    FriendRequestReceivedSerializer,
    FriendRequestSentSerializer,
    ProfileSerializer,
    LoginWithGoogleSerializer,
)


class ProfileView(generics.RetrieveAPIView, generics.UpdateAPIView):
    """
    Handles retrieving and updating the authenticated user's profile.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        """Returns the profile of the authenticated user."""
        return self.request.user.profile


class RegisterView(generics.CreateAPIView):
    """
    Handles user registration.
    """
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class LoginView(generics.GenericAPIView):
    """
    Handles user login and returns user data and authentication token.
    """
    serializer_class = LoginSerializer

    def post(self, request):
        """Validates the login data and returns user data and authentication token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })


class RetrieveGoogleAuthenticationURLView(views.APIView):
    """
    Retrieves the Google authentication URL.
    """

    def get(self, request, *args, **kwargs):
        """Builds the redirect URI and returns the Google authentication URL."""
        redirect_uri = request.build_absolute_uri('https://hang-coherentboi.vercel.app/auth')
        authorization_url = GoogleAuthenticationToken.get_authorization_url(redirect_uri)
        return Response({"authorization_url": authorization_url}, status=status.HTTP_200_OK)


class LoginWithGoogleView(views.APIView):
    """
    Handles user login with Google and returns user data and authentication token.
    """

    def post(self, request):
        """Validates the Google login data and returns user data and authentication token."""
        serializer = LoginWithGoogleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })


class RetrieveUserView(generics.RetrieveAPIView):
    """
    Retrieves the profile of a specific user or the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    lookup_field = None

    def get_object(self):
        """Returns the profile of a specific user or the authenticated user based on the lookup field."""
        if self.lookup_field == "me":
            return self.request.user.profile

        lookup_value = self.kwargs.get("lookup_value")

        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: lookup_value}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return obj.profile


class EmailVerificationTokenViewSet(viewsets.GenericViewSet):
    """
    Handles the creation and verification of email authentication tokens.
    """
    serializer_class = EmailAuthenticationTokenSerializer

    def get_queryset(self):
        """Returns the queryset of email authentication tokens."""
        return EmailAuthenticationToken.objects.filter(
            token=EmailAuthenticationToken.hash_token(self.kwargs.get("pk"))).all()

    def get_object(self):
        """Returns a specific email authentication token."""
        return get_object_or_404(self.get_queryset())

    def create(self, request, *args, **kwargs):
        """Creates a new email authentication token."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        """Verifies an email authentication token."""
        token = self.get_object()
        token.verify()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendRequestSentViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin, mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    """
    Handles the creation, retrieval, deletion, and listing of sent friend requests.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestSentSerializer

    def get_queryset(self):
        """Returns the queryset of sent friend requests."""
        return FriendRequest.objects.filter(from_user=self.request.user).all()

    def get_object(self):
        """Returns a specific sent friend request."""
        query = FriendRequest.objects.filter(from_user=self.request.user,
                                             to_user=self.kwargs["pk"])
        return get_object_or_404(query)


class FriendRequestReceivedViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin,
                                   viewsets.GenericViewSet):
    """
    Handles the listing, retrieval, acceptance, and declination of received friend requests.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestReceivedSerializer

    def get_queryset(self):
        """Returns the queryset of received friend requests."""
        return FriendRequest.objects.filter(to_user=self.request.user).all()

    def get_object(self):
        """Returns a specific received friend request."""
        query = FriendRequest.objects.filter(from_user_id=self.kwargs["pk"],
                                             to_user=self.request.user,
                                             declined=False)
        return get_object_or_404(query)

    def partial_update(self, request, *args, **kwargs):
        """Declines a received friend request."""
        instance = self.get_object()
        instance.decline_friend_request()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        """Accepts a received friend request."""
        instance = self.get_object()
        instance.accept_friend_request()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendsViewSet(viewsets.GenericViewSet):
    """
    Handles the listing and removal of friends.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        """Returns the queryset of friends."""
        return self.request.user.profile.friends.all()

    def list(self, request):
        """Returns a list of friend IDs."""
        return Response([friend.id for friend in self.get_queryset()], status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        """Removes a friend."""
        self.request.user.profile.remove_friend(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlockedUsersViewSet(viewsets.GenericViewSet):
    """
    Handles the listing, blocking, and unblocking of users.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        """Returns the queryset of blocked users."""
        return self.request.user.profile.blocked_users.all()

    def list(self, request):
        """Returns a list of blocked user IDs."""
        return Response([friend.id for friend in self.get_queryset()], status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        """Blocks a user."""
        user_to_block = get_object_or_404(User.objects.filter(id=request.data["id"]))
        self.request.user.profile.block_user(user_to_block)
        return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        """Unblocks a user."""
        self.request.user.profile.unblock_user(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)
