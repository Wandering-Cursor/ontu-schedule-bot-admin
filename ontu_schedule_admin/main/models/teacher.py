from django.db import models

from main.models.base import BaseModel


class Teacher(BaseModel):
    """
    Teachers represent academic staff members within the institution.
    """

    external_id = models.CharField(max_length=255, unique=True)

    short_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=1024)

    departments = models.ManyToManyField(
        "Department",
        related_name="teachers_m2m",
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.short_name} ({self.full_name}) - ID: {self.external_id}"

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=["uuid", "external_id"]),
        ]
