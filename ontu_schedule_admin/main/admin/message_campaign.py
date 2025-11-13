from django.contrib.admin import register

from main.models.message_campaign import MessageCampaign

from .base import BaseModelAdmin


@register(MessageCampaign)
class MessageCampaignAdmin(BaseModelAdmin):
    list_display_extra = ("name",)
