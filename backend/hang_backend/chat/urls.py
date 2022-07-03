# chat/urls.py
from django.urls import path

from . import views

urlpatterns = [
    path('load/', views.LoadMessage.as_view(), name='LoadMessage'),
    path('open_dm/', views.CreateDM.as_view(), name='open_dm'),
]
