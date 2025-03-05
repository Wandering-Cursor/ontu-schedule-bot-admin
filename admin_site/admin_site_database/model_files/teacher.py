"""
Teachers model, for teachers schedule
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db import models

from .base import BaseModel

if TYPE_CHECKING:
    from .department import Department


class Teacher(BaseModel):
    external_id = models.CharField(max_length=255, unique=True)
    short_name = models.CharField(max_length=255)
    full_name = models.TextField()

    department: "Department" = models.ForeignKey(
        "Department",
        on_delete=models.CASCADE,
        related_name="teachers",
    )
    departments: "models.ManyToManyField[Department]" = models.ManyToManyField(
        "Department",
        related_name="teachers_m2m",
    )

    def as_json(self) -> dict[str, str]:
        return {
            "external_id": self.external_id,
            "short_name": self.short_name,
            "full_name": self.full_name,
            "department": self.department.as_json(),
            "departments": [
                department.as_json() for department in self.departments.all()
            ],
        }

    def __str__(self) -> str:
        return f"{self.short_name} - {self.department}"
