from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from . import views

chat_management = [
    path("chat_info", views.ChatInfoView.ChatInfoView.as_view()),
    path("chat_create", views.ChatCreateView.ChatCreateView.as_view()),
    path("chats_all", views.ChatsAllView.ChatsAllView.as_view()),
    path("chat_update", views.ChatUpdateView.ChatUpdateView.as_view()),
]

get_methods = [
    path("faculties_get", views.FacultiesGetView.FacultiesGetView.as_view()),
    path("groups_get", views.GroupsGetView.GroupsGetView.as_view()),
    path(
        "teachers/department",
        views.TeachersDepartmentView.TeachersDepartmentView.as_view(),
    ),
    path(
        "teachers/departments",
        views.TeachersDepartmentsView.TeachersDepartmentsView.as_view(),
    ),
]

tech = [
    path("update_notbot", views.UpdateNotbotView.UpdateNotbotView.as_view()),
    path("reset_cache", views.ResetCacheView.ResetCacheView.as_view()),
    path(
        "teachers/reset_cache",
        views.ResetTeachersCacheView.ResetTeachersCacheView.as_view(),
    ),
    path(
        "message_campaign",
        views.MessageCampaignView.GetMessageCampaign.as_view(),
    ),
]

schedule_get = [
    path("schedule_get", views.ScheduleGetView.ScheduleGetView.as_view()),
    path("batch_schedule", views.BatchScheduleView.BatchScheduleView.as_view()),
    path(
        "teachers/schedule", views.TeachersScheduleView.TeachersScheduleView.as_view()
    ),
]

schema_views = [
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

urlpatterns = chat_management + get_methods + tech + schedule_get + schema_views
