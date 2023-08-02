from django.urls import path

from . import views

urlpatterns = [
    path('chat_info', views.ChatInfoView.as_view()),
    path('chat_create', views.ChatCreateView.as_view()),
    path('chats_all', views.ChatsAllView.as_view()),

    path('chat_update', views.ChatUpdateView.as_view()),

    path('faculties_get', views.FacultiesGetView.as_view()),
    path('groups_get', views.GroupsGetView.as_view()),
    path('update_notbot', views.UpdateNotbotView.as_view()),
    path('reset_cache', views.ResetCacheView.as_view()),

    path('schedule_get', views.ScheduleGetView.as_view()),
]
