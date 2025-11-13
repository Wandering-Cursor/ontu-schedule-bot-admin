from django.db import models

from main.models.base import BaseModel


class Department(BaseModel):
    """
    Departments are grouping Teachers by their academic department.
    """

    external_id = models.CharField(max_length=255, unique=True)

    short_name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=1024)

    def __str__(self) -> str:
        return f"{self.short_name} ({self.full_name}) - ID: {self.external_id}"

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=["uuid", "external_id"]),
        ]
