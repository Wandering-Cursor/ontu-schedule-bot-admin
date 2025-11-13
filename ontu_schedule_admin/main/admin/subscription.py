from django.contrib.admin import register

from main.models.subscription import Subscription

from .base import BaseModelAdmin


@register(Subscription)
class SubscriptionAdmin(BaseModelAdmin):
    list_display_extra = ("is_active",)
