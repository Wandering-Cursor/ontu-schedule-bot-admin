from django.contrib import admin
from django.http.request import HttpRequest
from djangoql.admin import DjangoQLSearchMixin

from .models import ScheduleCache


class BaseAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
    """
    Base Admin Class. Use it as basis for other admin sites
    """

    def get_list_display(self, request: HttpRequest):
        return [field.name for field in self.Meta.model._meta.get_fields()]


@admin.register(ScheduleCache)
class ScheduleCacheAdmin(BaseAdmin):
    class Meta:
        model = ScheduleCache
