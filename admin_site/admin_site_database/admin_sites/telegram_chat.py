"""
Admin Site for Subscription
"""
from admin_site_database.admin_sites.base import BaseAdmin
from admin_site_database.model_files import TelegramChat
from django.contrib import admin


@admin.register(TelegramChat)
class TelegramChatAdmin(BaseAdmin):
    """
    Admin site for Telegram Chats.
    """

    list_display = BaseAdmin.list_display + [
        "telegram_id",
        "name",
        "is_forum",
        "topic_id",
        "subscription",
        "chat_info",
    ]

    readonly_fields = BaseAdmin.readonly_fields + [
        "telegram_id",
        "topic_id",
        "chat_info",
    ]
