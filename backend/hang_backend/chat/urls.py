# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('load/', views.load_past_messages, name='load_past_messages')
]
