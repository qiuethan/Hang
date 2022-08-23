from django.urls import path
from knox import views as knox_views

from .views import LoginView, RegisterView, RetrieveCurrentUserView, SendEmailView, VerifyEmailView, ListFriendsView, \
    ListCreateBlockedUsersView, ListCreateSentFriendRequestView, RetrieveDestroySentFriendRequestView, \
    ListReceivedFriendRequestView, RetrieveUpdateDestroyReceivedFriendRequestView, RemoveFriendsView, \
    RemoveBlockedUsersView, RetrieveUserView

app_name = "accounts"

urlpatterns = [
    path("register", RegisterView.as_view()),
    path("login", LoginView.as_view()),
    path("logout", knox_views.LogoutView.as_view(), name="knox_logout"),
    path("user/<str:pk>", RetrieveUserView.as_view()),
    path("current_user", RetrieveCurrentUserView.as_view()),
    path("send_email", SendEmailView.as_view()),
    path("verify_email", VerifyEmailView.as_view()),
    path("sent_friend_request", ListCreateSentFriendRequestView.as_view()),
    path("sent_friend_request/<str:user_id>", RetrieveDestroySentFriendRequestView.as_view()),
    path("received_friend_request", ListReceivedFriendRequestView.as_view()),
    path("received_friend_request/<str:user_id>", RetrieveUpdateDestroyReceivedFriendRequestView.as_view()),
    path("friends", ListFriendsView.as_view()),
    path("friends/<str:pk>", RemoveFriendsView.as_view()),
    path("blocked_users", ListCreateBlockedUsersView.as_view()),
    path("blocked_users/<str:pk>", RemoveBlockedUsersView.as_view()),
]
