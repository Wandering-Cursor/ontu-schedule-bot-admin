"""
Teachers model, for teachers schedule
"""


from django.db import models

from .base import BaseModel


class Teacher(BaseModel):
    external_id = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=255)
    full_name = models.TextField()

    department = models.ForeignKey(
        "Department",
        on_delete=models.CASCADE,
        related_name="teachers",
    )

    def as_json(self) -> dict[str, str]:
        return {
            "external_id": self.external_id,
            "short_name": self.short_name,
            "full_name": self.full_name,
            "department": self.department.as_json(),
        }
