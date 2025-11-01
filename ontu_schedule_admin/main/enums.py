from django.db import models


class Platform(models.TextChoices):
    TELEGRAM = "TELEGRAM", "Telegram"
