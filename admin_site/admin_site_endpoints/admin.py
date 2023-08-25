from django.contrib import admin

from djangoql.admin import DjangoQLSearchMixin

from .models import ScheduleCache


class BaseAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    """
    Base Admin Class. Use it as basis for other admin sites
    """
    pass


@admin.register(ScheduleCache)
class ScheduleCacheAdmin(BaseAdmin):
    list_display = [
        'faculty',
        'group',
        'schedule',
        'at_time'
    ]
