from django.contrib.auth.models import User
from django.db import models


class FriendRequest(models.Model):
    """Model that represents a friend request object."""
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_friend_requests")
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_friend_requests")
    declined = models.BooleanField(default=False)  # Shows whether the friend request has been declined by `to_user`.


class EmailAuthToken(models.Model):
    """Model that represents an email authentication token. Used to verify a user's account."""
    id = models.CharField(max_length=64, primary_key=True) # Token is stored as SHA256 hash.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class UserDetails(models.Model):
    """Additional settings / details about a user."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    profile_picture = models.CharField(max_length=200, default="default profile pic change this later")  # TODO: CHANGE
    is_verified = models.BooleanField(default=False)  # Shows whether the user has been verified by email.
    about_me = models.TextField(default="")

    friends = models.ManyToManyField(User, related_name="+")
    blocked_users = models.ManyToManyField(User, related_name="+")
