"""
Admin Site for Subscription
"""
from django.contrib import admin


from admin_site_database.model_files import TelegramChat
from admin_site_database.admin_sites.base import BaseAdmin


@admin.register(TelegramChat)
class TelegramChatAdmin(BaseAdmin):
    """
    Admin site for Telegram Chats.
    """
    list_display = BaseAdmin.list_display + [
        'telegram_id',
        'name',
        'subscription',
        'chat_info'
    ]

    readonly_fields = BaseAdmin.readonly_fields + [
        'telegram_id',
        'chat_info'
    ]
