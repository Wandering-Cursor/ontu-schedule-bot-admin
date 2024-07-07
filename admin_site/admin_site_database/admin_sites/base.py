"""
Base Admin class. Provides handy lists and ordering
"""

from django.contrib import admin
from djangoql.admin import DjangoQLSearchMixin


class BaseAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    """
    Base Admin Class. Use it as basis for other admin sites
    """

    list_display = ["id", "created", "updated"]

    readonly_fields = ["id", "created", "updated"]

    ordering = ["-created"]
