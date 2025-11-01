from main.models.base import BaseModel
from django.db import models


class Subscription(BaseModel):
    chats = models.ManyToManyField(
        "Chat",
        related_name="subscriptions",
        blank=True,
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
