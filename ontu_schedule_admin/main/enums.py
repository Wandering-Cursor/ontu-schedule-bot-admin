from enum import StrEnum

from django.db import models


class Platform(models.TextChoices):
    TELEGRAM = "TELEGRAM", "Telegram"


class ScheduleEntityType(StrEnum):
    GROUP = "group"
    TEACHER = "teacher"
