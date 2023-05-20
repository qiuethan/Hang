from django.contrib.auth.models import User
from django.http import JsonResponse
from knox.models import AuthToken
from rest_framework import generics, permissions, status, views, viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT

from .models import EmailAuthenticationToken, FriendRequest, Profile, GoogleAuthenticationToken
from .serializers import LoginSerializer, UserSerializer, RegisterSerializer, EmailAuthenticationTokenSerializer, \
    FriendRequestReceivedSerializer, FriendRequestSentSerializer, ProfileSerializer, \
    LoginWithGoogleSerializer


class ProfileView(generics.RetrieveAPIView, generics.UpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.profile


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })


class RetrieveGoogleAuthenticationURLView(views.APIView):
    def get(self, request, *args, **kwargs):
        redirect_uri = request.build_absolute_uri('http://localhost:3000/profile')
        authorization_url = GoogleAuthenticationToken.get_authorization_url(redirect_uri)
        return Response({"authorization_url": authorization_url}, status=status.HTTP_200_OK)


class LoginWithGoogleView(views.APIView):

    def post(self, request):
        serializer = LoginWithGoogleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })


class RetrieveUserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    lookup_field = None

    def get_object(self):
        if self.lookup_field == "me":
            return self.request.user.profile

        lookup_value = self.kwargs.get("lookup_value")

        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: lookup_value}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return obj.profile


class EmailVerificationTokenViewSet(viewsets.GenericViewSet):
    serializer_class = EmailAuthenticationTokenSerializer

    def get_queryset(self):
        return EmailAuthenticationToken.objects.filter(
            token=EmailAuthenticationToken.hash_token(self.kwargs.get("pk"))).all()

    def get_object(self):
        return get_object_or_404(self.get_queryset())

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        token = self.get_object()
        token.verify()
        return Response(status=status.HTTP_204_NO_CONTENT)


class SentFriendRequestViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.ListModelMixin,
                               viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestSentSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(from_user=self.request.user).all()

    def get_object(self):
        query = FriendRequest.objects.filter(from_user=self.request.user,
                                             to_user=self.kwargs["pk"])
        return get_object_or_404(query)


class ReceivedFriendRequestViewSet(mixins.ListModelMixin,
                                   mixins.RetrieveModelMixin,
                                   viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FriendRequestReceivedSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user).all()

    def get_object(self):
        query = FriendRequest.objects.filter(from_user_id=self.kwargs["pk"],
                                             to_user=self.request.user,
                                             declined=False)
        return get_object_or_404(query)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.decline_friend_request()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.accept_friend_request()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendsViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.profile.friends.all()

    def list(self, request):
        return Response([friend.id for friend in self.get_queryset()], status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        self.request.user.profile.remove_friend(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlockedUsersViewSet(viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.profile.blocked_users.all()

    def list(self, request):
        return Response([friend.id for friend in self.get_queryset()], status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        user_to_block = get_object_or_404(User.objects.filter(id=request.data["id"]))
        self.request.user.profile.block_user(user_to_block)
        return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        self.request.user.profile.unblock_user(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)
