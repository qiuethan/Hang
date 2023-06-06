from django.urls import path
from knox import views as knox_views
from rest_framework.routers import DefaultRouter

from .views import (
    LoginView, RegisterView,
    LoginWithGoogleView,
    RetrieveGoogleAuthenticationURLView, RetrieveUserView, FriendRequestSentViewSet, FriendRequestReceivedViewSet,
    FriendsViewSet, BlockedUsersViewSet, EmailVerificationTokenViewSet, ProfileView
)

app_name = "accounts"

router = DefaultRouter()
router.register(r'friend_requests/sent', FriendRequestSentViewSet, basename='sent_friend_requests')
router.register(r'friend_requests/received', FriendRequestReceivedViewSet, basename='received_friend_requests')
router.register(r'friends', FriendsViewSet, basename='friends')
router.register(r'blocked_users', BlockedUsersViewSet, basename='blocked_users')
router.register(r'email_verification_tokens', EmailVerificationTokenViewSet, basename='email_verification_tokens')

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path('login/google/url/', RetrieveGoogleAuthenticationURLView.as_view(), name='retrieve_authorization_url'),
    path("login/google/", LoginWithGoogleView.as_view(), name="login_with_google"),
    path("logout/", knox_views.LogoutView.as_view(), name="logout"),

    path("users/id/<str:lookup_value>/", RetrieveUserView.as_view(lookup_field="id"), name="user_me"),
    path("users/email/<str:lookup_value>/", RetrieveUserView.as_view(lookup_field="email"), name="user_email"),
    path("users/username/<str:lookup_value>/", RetrieveUserView.as_view(lookup_field="username"), name="user_username"),
    path("users/me/", ProfileView.as_view(), name="user_me"),
]

urlpatterns += router.urls
