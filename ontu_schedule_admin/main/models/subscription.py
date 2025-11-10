from typing import TYPE_CHECKING

from django.db import models

from main.models.base import BaseModel

if TYPE_CHECKING:
    from main.models.chat import Chat


class Subscription(BaseModel):
    is_active = models.BooleanField(
        default=True,
    )

    groups = models.ManyToManyField(
        "Group",
        related_name="subscriptions",
        blank=True,
    )
    teachers = models.ManyToManyField(
        "Teacher",
        related_name="subscriptions",
        blank=True,
    )

    chat: Chat

    def __str__(self) -> str:
        return f"Subscription {self.uuid} - Active: {self.is_active}"

    class Meta(BaseModel.Meta):
        pass
