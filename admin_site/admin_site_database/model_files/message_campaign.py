"""
A message campaign (mass-sending of messages)
"""

from django.db import models
from django.utils.safestring import mark_safe

from admin_site_database.model_files.base import BaseModel
from admin_site_database.model_files.telegram_chat import TelegramChat


class MessageCampaign(BaseModel):
    """
    A message campaign is a certain text sent to some chats

    Raises:
        NotImplementedError: if you call as_json
    """

    bot_key = models.CharField(
        max_length=128,
        blank=False,
        null=False,
    )
    to_chats = models.ManyToManyField(
        to=TelegramChat,
        blank=False,
    )

    def as_json(self) -> dict[str, list[str] | str]:
        return {
            "to_chats": [chat.telegram_id for chat in self.to_chats.all()],
            "message": self.message,
        }

    message = models.TextField(max_length=4096)

    @property
    def safe_bot_key(self):
        """Last few characters of bot_key"""
        safe_key = ""
        safe_key += self.bot_key[-6:]
        return safe_key

    @property
    def cropped_message(self):
        """First 128 chars of message"""
        message = self.message[:128]
        if len(self.message) > 128:
            message += "..."
        return mark_safe(message)

    @property
    def get_to_chats(self):
        return list(self.to_chats.all())  # type: ignore
