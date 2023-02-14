"""Stores all models for admin"""
from django.db import models

from django.utils import timezone

import admin_site_database.db as admin_db
import uuid


class BaseModel(models.Model):
    """Base model for all the others. Contains some common params"""
    id = models.UUIDField(primary_key=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        if not self.created:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class Settings(BaseModel):
    """Model for various settings in app"""
    name = models.TextField()

    value = models.TextField()

    objects = admin_db.SettingsManager


class Faculty(BaseModel):
    """Model for Faculty on Schedule site"""
    name = models.TextField()

    objects = admin_db.FacultyManager()

    def as_json(self):
        return {"name": self.name}

    def __str__(self) -> str:
        return f"Faculty: {self.name}"


class Group(BaseModel):
    """Model for Group on Schedule site, Group is located inside a Faculty"""
    name = models.TextField()
    faculty = models.ForeignKey(
        to=Faculty,
        on_delete=models.CASCADE,
        related_name="groups"
    )

    def as_json(self):
        return {'name': self.name, 'faculty': self.faculty.as_json()}

    objects = admin_db.GroupManager

    def __str__(self) -> str:
        return f"Group: {self.name} - {self.faculty}"


class Subscription(BaseModel):
    """Model for tracking schedule subscriptions for chats"""
    is_active = models.BooleanField()
    group = models.ForeignKey(
        to=Group,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    def as_json(self):
        return {
            'is_active': self.is_active,
            'group': self.group.as_json(),
        }

    @property
    def related_telegram_chats(self):
        """Returns related telegram chats"""
        telegram_chats = getattr(self, 'telegram_chats', None)
        if not hasattr(telegram_chats, 'all'):
            return None
        subscribed_chats = telegram_chats.all()
        if not subscribed_chats:
            return None
        return list(subscribed_chats)

    objects = admin_db.SubscriptionManager


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
        related_name="telegram_chats"
    )
    chat_info = models.JSONField(
        blank=True,
        null=True
    )

    objects = admin_db.TelegramChatManager

    def as_json(self):
        data = {
            'chat_id': self.telegram_id,
            'chat_name': self.name,
        }
        self.subscription: Subscription
        if self.subscription:
            data['subscription'] = self.subscription.as_json()
        return data

    def __str__(self) -> str:
        return f"{self.name} - {self.telegram_id}"
