from django.urls import path
from knox import views as knox_views

from .views import LoginAPI, RegisterAPI, UserAPI, SendEmail, VerifyEmail

urlpatterns = [
    path('register', RegisterAPI.as_view()),
    path('login', LoginAPI.as_view()),
    path('logout', knox_views.LogoutView.as_view(), name='knox_logout'),
    path('user', UserAPI.as_view()),
    path('send_email', SendEmail.as_view()),
    path('verify_email', VerifyEmail.as_view()),
]