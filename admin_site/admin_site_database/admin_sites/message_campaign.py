"""
Message Campaign site
"""

from django.contrib import admin

from admin_site_database.model_files import MessageCampaign

from .base import BaseAdmin


@admin.register(MessageCampaign)
class MessageCampaignAdmin(BaseAdmin):
    """
    Message Campaign Admin site
    """

    list_display = BaseAdmin.list_display + [
        'get_to_chats',
        'safe_bot_key',
        'cropped_message',
    ]

    readonly_fields = BaseAdmin.readonly_fields
