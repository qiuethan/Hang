# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('create_dm/', views.CreateDMView.as_view(), name='CreateDM'),
    path('create_gc/', views.CreateGCView.as_view(), name='CreateGC'),
    path('modify_gc/', views.ModifyGCView.as_view(), name='ModifyGC'),
    path('list_channels/', views.ListMessageChannelsView.as_view(), name='ListMessageChannels'),
]
