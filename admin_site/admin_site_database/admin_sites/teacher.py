from .base import BaseAdmin
from admin_site_database.model_files import Teacher
from django.contrib import admin


class TeacherAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + [
        "external_id",
        "short_name",
        "full_name",
        "department",
    ]


admin.site.register(Teacher, TeacherAdmin)
