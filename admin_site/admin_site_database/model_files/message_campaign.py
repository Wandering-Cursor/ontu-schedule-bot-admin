"""
A message campaign (mass-sending of messages)
"""
import requests

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

    def as_json(self):
        raise NotImplementedError(
            "You should not call as_json for MessageCampaign objects"
        )

    message = models.TextField(max_length=4096)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        telegram_api_url = f"https://api.telegram.org/bot{self.bot_key}/sendMessage"

        # You have to save campaign and then resave it to send messages
        for chat in self.to_chats.all():  # type: ignore
            chat: TelegramChat
            response = requests.get(
                url=telegram_api_url,
                data={
                    'chat_id': chat.telegram_id,
                    'text': self.message,
                    'parse_mode': 'HTML'
                },
                timeout=5
            )

    @property
    def safe_bot_key(self):
        """Last few characters of bot_key"""
        safe_key = ''
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
        return list(self.to_chats.all())  #type: ignore
