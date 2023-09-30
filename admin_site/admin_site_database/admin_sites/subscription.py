"""
Admin Site for Subscription
"""
from django.contrib import admin


from admin_site_database.model_files import Subscription
from admin_site_database.admin_sites.base import BaseAdmin


@admin.register(Subscription)
class SubscriptionAdmin(BaseAdmin):
    """
    Admin site for Subscription.
    Also shows related telegram chats.
    """

    list_display = BaseAdmin.list_display + [
        "is_active",
        "group",
        "teacher",
        "get_telegram_chats",
    ]

    def get_telegram_chats(self, obj: Subscription):
        """Returns related chats per subscription object

        Args:
            obj (models.Subscription): A subscription to schedule

        Returns:
            list | None: List of related Telegram Chats or None
        """
        return obj.related_telegram_chats
