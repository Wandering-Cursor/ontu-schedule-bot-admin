"""
A model for the department table in the database.
Used in teachers schedule.
"""

from django.db import models

from .base import BaseModel


class Department(BaseModel):
    """Model for department on schedule site"""

    external_id = models.CharField(max_length=255, unique=True)
    short_name = models.TextField()
    full_name = models.TextField()

    def as_json(self):
        return {
            "external_id": self.external_id,
            "name": self.short_name,
            "full_name": self.full_name,
        }

    def __str__(self) -> str:
        return f"Department: {self.short_name}"
