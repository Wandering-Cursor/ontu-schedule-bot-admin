from django.contrib import admin

from admin_site_database.model_files import TeacherScheduleCache

from .base import BaseAdmin


class TeacherScheduleCacheAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + [
        "teacher",
        "department",
        "schedule",
    ]
    list_filter = [
        "teacher",
    ]


admin.site.register(TeacherScheduleCache, TeacherScheduleCacheAdmin)
