from django.contrib.admin import register

from main.models.department import Department

from .base import BaseModelAdmin


@register(Department)
class DepartmentAdmin(BaseModelAdmin):
    list_display_extra = (
        "external_id",
        "short_name",
    )
