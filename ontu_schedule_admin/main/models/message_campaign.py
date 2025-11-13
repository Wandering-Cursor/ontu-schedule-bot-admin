from django.db import models

from main.models.base import BaseModel


class MessageCampaign(BaseModel):
    """
    MessageCampaigns represent scheduled messaging campaigns within the system.

    They are sent on-demand to specified recipients (or all Chats if no recipients are specified).
    """

    name = models.CharField(max_length=512)

    # Stores some data about the message to be sent.
    # Like if it's a text message, image, etc., and the content itself.
    payload = models.JSONField()

    recipients = models.ManyToManyField(
        "Chat",
        related_name="message_campaigns_m2m",
        blank=True,
    )

    class Meta(BaseModel.Meta):
        pass
