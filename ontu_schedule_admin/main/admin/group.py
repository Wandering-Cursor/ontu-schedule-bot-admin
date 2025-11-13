from django.contrib.admin import register

from main.models.group import Group

from .base import BaseModelAdmin


@register(Group)
class GroupAdmin(BaseModelAdmin):
    list_display_extra = (
        "short_name",
        "faculty",
    )
