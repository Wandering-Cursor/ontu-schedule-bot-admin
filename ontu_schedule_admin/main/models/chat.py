from django.db import models

from main.enums import Platform
from main.models.base import BaseModel


class Chat(BaseModel):
    platform = models.CharField(
        max_length=255,
        choices=Platform.choices,
    )

    platform_chat_id = models.CharField(max_length=255)

    title = models.CharField(max_length=255, blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    language_code = models.CharField(max_length=2, blank=True, null=True)

    # Used to store any additional platform-specific information
    # for example, on Telegram - `topic_id`, `is_forum`, etc.
    additional_info = models.JSONField(blank=True, null=True)

    subscription = models.OneToOneField(
        "Subscription",
        on_delete=models.CASCADE,
        related_name="chat",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.platform} - {self.platform_chat_id}"

    class Meta(BaseModel.Meta):
        unique_together = ("platform", "platform_chat_id")
