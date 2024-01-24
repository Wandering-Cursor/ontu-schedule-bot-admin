"""
Subscription Model
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from admin_site_database import db as admin_db
from admin_site_database.model_files.base import BaseModel
from admin_site_database.model_files.group import Group
from django.db import models

if TYPE_CHECKING:
    from admin_site_database.model_files.teacher import Teacher
    from admin_site_database.model_files.telegram_chat import TelegramChat


class Subscription(BaseModel):
    """Model for tracking schedule subscriptions for chats"""

    is_active = models.BooleanField()
    group: "Group" = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,
        blank=True,
    )
    teacher: "Teacher" = models.ForeignKey(
        to="Teacher",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        null=True,
        blank=True,
    )

    def as_json(self):
        return {
            "is_active": self.is_active,
            "group": self.group.as_json() if self.group else None,
            "teacher": self.teacher.as_json() if self.teacher else None,
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
        return f"To: {self.group} | {self.teacher}"

    objects = admin_db.SubscriptionManager
