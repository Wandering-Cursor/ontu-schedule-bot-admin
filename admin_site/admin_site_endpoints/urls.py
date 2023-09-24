from django.urls import path

from . import views

chat_management = [
    path("chat_info", views.ChatInfoView.as_view()),
    path("chat_create", views.ChatCreateView.as_view()),
    path("chats_all", views.ChatsAllView.as_view()),
    path("chat_update", views.ChatUpdateView.as_view()),
]

get_methods = [
    path("faculties_get", views.FacultiesGetView.as_view()),
    path("groups_get", views.GroupsGetView.as_view()),
    path("teachers/department", views.TeachersDepartmentView.as_view()),
    path("teachers/departments", views.TeachersDepartmentsView.as_view()),
]

tech = [
    path("update_notbot", views.UpdateNotbotView.as_view()),
    path("reset_cache", views.ResetCacheView.as_view()),
    path("teachers/reset_cache", views.ResetTeachersCacheView.as_view()),
]

schedule_get = [
    path("schedule_get", views.ScheduleGetView.as_view()),
    path("batch_schedule", views.BatchScheduleView.as_view()),
    path("teachers/schedule", views.TeachersScheduleView.as_view()),
]

urlpatterns = chat_management + get_methods + tech + schedule_get
