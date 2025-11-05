from django.contrib.admin import register

from main.models.teacher import Teacher

from .base import BaseModelAdmin


@register(Teacher)
class TeacherAdmin(BaseModelAdmin):
    list_display_extra = (
        "external_id",
        "short_name",
        "full_name",
    )
