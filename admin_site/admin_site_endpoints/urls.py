from django.urls import path

from . import views

urlpatterns = [
    path('chat_info', views.ChatInfoView.as_view()),
    path('chat_create', views.ChatCreateView.as_view()),
]
