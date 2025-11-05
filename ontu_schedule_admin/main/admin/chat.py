from django.contrib.admin import register

from main.models.chat import Chat

from .base import BaseModelAdmin


@register(Chat)
class ChatAdmin(BaseModelAdmin):
    list_display_extra = (
        "platform",
        "platform_chat_id",
        "title",
        "username",
    )
    readonly_fields = (*BaseModelAdmin.readonly_fields, "additional_info")
