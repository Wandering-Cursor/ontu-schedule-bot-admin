"""
Telegram Chat model
"""

from django.db import models

from admin_site_database import db as admin_db
from admin_site_database.model_files.base import BaseModel
from admin_site_database.model_files.subscription import Subscription


class TelegramChat(BaseModel):
    """
    Model that keeps Telegram Chat in our base
    Chat is either a person, or a group
    Chat should receive schedule if they have a subscription
    """

    telegram_id = models.BigIntegerField()
    name = models.TextField()

    subscription = models.ForeignKey(
        to=Subscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="telegram_chats",
    )
    chat_info = models.JSONField(blank=True, null=True)

    is_forum = models.BooleanField(default=False)
    topic_id = models.IntegerField(blank=True, null=True)

    objects = admin_db.TelegramChatManager

    def as_json(self):
        data = {
            "chat_id": self.telegram_id,
            "chat_name": self.name,
        }
        # I'm not sure how to handle this properly :|
        self.subscription: Subscription
        if self.subscription:
            data["subscription"] = self.subscription.as_json()
        return data

    def __str__(self) -> str:
        return f"{self.name} - {self.telegram_id}"
