"""
Subscription Model
"""
from __future__ import annotations
from typing import TYPE_CHECKING
from django.db import models

from admin_site_database import db as admin_db
from admin_site_database.model_files.base import BaseModel
from admin_site_database.model_files.group import Group

if TYPE_CHECKING:
    from admin_site_database.model_files.telegram_chat import TelegramChat


class Subscription(BaseModel):
    """Model for tracking schedule subscriptions for chats"""

    is_active = models.BooleanField()
    group = models.ForeignKey(to=Group, on_delete=models.CASCADE, related_name="subscriptions")

    def as_json(self):
        # I'm not sure how to handle this properly :|
        self.group: Group
        return {
            "is_active": self.is_active,
            "group": self.group.as_json(),
        }

    @property
    def related_telegram_chats(self) -> "list[TelegramChat]":
        """Returns related telegram chats"""
        telegram_chats = getattr(self, "telegram_chats", None)
        if not hasattr(telegram_chats, "all"):
            return None
        subscribed_chats = telegram_chats.all()
        if not subscribed_chats:
            return None
        return list(subscribed_chats)

    def __str__(self) -> str:
        return f"To: {self.group.name}"

    objects = admin_db.SubscriptionManager
