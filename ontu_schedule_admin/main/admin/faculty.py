from django.contrib.admin import register

from main.models.faculty import Faculty

from .base import BaseModelAdmin


@register(Faculty)
class FacultyAdmin(BaseModelAdmin):
    list_display_extra = ("short_name",)
