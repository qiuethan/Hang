from django.urls import path
from knox import views as knox_views

from .views import (
    LoginView, RegisterView, RetrieveCurrentUserView, SendVerificationEmailView,
    VerifyEmailVerificationTokenView, ListFriendsView, ListCreateBlockedUsersView,
    ListCreateSentFriendRequestView, RetrieveDestroySentFriendRequestView,
    ListReceivedFriendRequestView, RetrieveAcceptDenyReceivedFriendRequestView,
    RemoveFriendsView, RemoveBlockedUsersView, RetrieveUserViewID,
    RetrieveUserViewEmail, RetrieveUserViewUsername, LoginWithGoogleView, UpdateAboutMeView, UpdateProfilePictureView
)

app_name = "accounts"

urlpatterns = [
    path("register", RegisterView.as_view(), name="register"),
    path("login", LoginView.as_view(), name="login"),
    path("login_with_google", LoginWithGoogleView.as_view(), name="login_with_google"),
    path("logout", knox_views.LogoutView.as_view(), name="logout"),
    path("user/id/<str:pk>", RetrieveUserViewID.as_view(), name="retrieve_user_id"),
    path("user/email/<str:email>", RetrieveUserViewEmail.as_view(), name="retrieve_user_email"),
    path("user/username/<str:username>", RetrieveUserViewUsername.as_view(), name="retrieve_user_username"),
    path('user/update_profile_picture/', UpdateProfilePictureView.as_view(), name='update_profile_picture'),
    path('user/update_about_me/', UpdateAboutMeView.as_view(), name='update_about_me'),
    path("current_user", RetrieveCurrentUserView.as_view(), name="retrieve_current_user"),
    path("send_email", SendVerificationEmailView.as_view(), name="send_verification_email"),
    path("verify_email", VerifyEmailVerificationTokenView.as_view(), name="verify_email_token"),
    path("sent_friend_request", ListCreateSentFriendRequestView.as_view(), name="list_create_sent_friend_request"),
    path("sent_friend_request/<str:user_id>", RetrieveDestroySentFriendRequestView.as_view(),
         name="retrieve_destroy_sent_friend_request"),
    path("received_friend_request", ListReceivedFriendRequestView.as_view(), name="list_received_friend_request"),
    path("received_friend_request/<str:user_id>", RetrieveAcceptDenyReceivedFriendRequestView.as_view(),
         name="retrieve_accept_deny_received_friend_request"),
    path("friends", ListFriendsView.as_view(), name="list_friends"),
    path("friends/<str:pk>", RemoveFriendsView.as_view(), name="remove_friend"),
    path("blocked_users", ListCreateBlockedUsersView.as_view(), name="list_create_blocked_users"),
    path("blocked_users/<str:pk>", RemoveBlockedUsersView.as_view(), name="remove_blocked_user"),
]
