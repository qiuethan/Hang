from django.contrib.auth.models import User
from django.http import JsonResponse
from knox.models import AuthToken
from rest_framework import generics, permissions, status, views, viewsets, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView

from common.util.generics.mixins import ListIDModelMixin
from .models import EmailAuthToken, FriendRequest, UserDetails, GoogleAuthenticationToken
from .serializers import LoginSerializer, UserSerializer, RegisterSerializer, SendEmailSerializer, \
    FriendRequestReceivedSerializer, FriendRequestSentSerializer, UserDetailsSerializer, \
    LoginWithGoogleSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()


class LoginView(views.APIView):

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return JsonResponse({
            "user": UserSerializer(user).data,
            "token": AuthToken.objects.create(user)[1]
        })


class RetrieveAuthorizationURLView(APIView):
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
    serializer_class = UserDetailsSerializer
    queryset = User.objects.all()
    lookup_field = None

    def get_object(self):
        if not self.lookup_field == "me":
            return self.request.user.userdetails

        lookup_value = self.kwargs.get("lookup_value")

        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: lookup_value}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)

        return obj.userdetails


class EmailVerificationTokenViewSet(viewsets.GenericViewSet):
    serializer_class = SendEmailSerializer

    def create(self, request, *args, **kwargs):
        serializer = SendEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        token = get_object_or_404(EmailAuthToken.objects.filter(token=EmailAuthToken.hash_token(self.kwargs["pk"])))
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

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.decline_friend_request()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.accept_friend_request()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FriendsViewSet(ListIDModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.userdetails.friends.all()

    def destroy(self, request, *args, **kwargs):
        self.request.user.userdetails.remove_friend(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlockedUsersViewSet(ListIDModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        return self.request.user.userdetails.blocked_users.all()

    def create(self, request, *args, **kwargs):
        query = User.objects.filter(id=request.data["id"])
        self.request.user.userdetails.block_user(get_object_or_404(query))
        return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request, *args, **kwargs):
        self.request.user.userdetails.unblock_user(self.get_object())
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserDetailsView(generics.RetrieveAPIView, generics.UpdateAPIView):
    queryset = UserDetails.objects.all()
    serializer_class = UserDetailsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.userdetails
