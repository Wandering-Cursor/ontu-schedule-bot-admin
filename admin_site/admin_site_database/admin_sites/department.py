from .base import BaseAdmin
from admin_site_database.model_files import Department
from django.contrib import admin


class DepartmentAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ["external_id", "short_name", "full_name"]


admin.site.register(Department, DepartmentAdmin)
