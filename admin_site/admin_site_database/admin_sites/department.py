from django.contrib import admin

from admin_site_database.model_files import Department

from .base import BaseAdmin


class DepartmentAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + ["external_id", "short_name", "full_name"]


admin.site.register(Department, DepartmentAdmin)
