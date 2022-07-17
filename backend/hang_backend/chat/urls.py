# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('create_dm/', views.CreateDMView.as_view(), name='CreateDM'),
    path('list_channels/', views.ListMessageChannelsView.as_view(), name='ListMessageChannels'),
]
