from django.urls import path
from knox import views as knox_views

from .views import LoginView, RegisterView, RetrieveCurrentUserView, SendVerificationEmailView, \
    VerifyEmailVerificationTokenView, ListFriendsView, \
    ListCreateBlockedUsersView, ListCreateSentFriendRequestView, RetrieveDestroySentFriendRequestView, \
    ListReceivedFriendRequestView, RetrieveAcceptDenyReceivedFriendRequestView, RemoveFriendsView, \
    RemoveBlockedUsersView, RetrieveUserViewID, RetrieveUserViewEmail, RetrieveUserViewUsername

app_name = "accounts"

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("logout", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("user/id/<str:pk>", RetrieveUserViewID.as_view()),
    path("user/email/<str:email>", RetrieveUserViewEmail.as_view()),
    path("user/username/<str:username>", RetrieveUserViewUsername.as_view()),
    path("current_user", RetrieveCurrentUserView.as_view()),
    path("send_email", SendVerificationEmailView.as_view()),
    path("verify_email", VerifyEmailVerificationTokenView.as_view()),
    path("sent_friend_request", ListCreateSentFriendRequestView.as_view()),
    path("sent_friend_request/<str:user_id>", RetrieveDestroySentFriendRequestView.as_view()),
    path("received_friend_request", ListReceivedFriendRequestView.as_view()),
    path("received_friend_request/<str:user_id>", RetrieveAcceptDenyReceivedFriendRequestView.as_view()),
    path("friends", ListFriendsView.as_view()),
    path("friends/<str:pk>", RemoveFriendsView.as_view()),
    path("blocked_users", ListCreateBlockedUsersView.as_view()),
    path("blocked_users/<str:pk>", RemoveBlockedUsersView.as_view()),
]
