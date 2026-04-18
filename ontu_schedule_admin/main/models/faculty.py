from django.db import models
from main.models.base import BaseModel


class Faculty(BaseModel):
    """
    Faculties are grouping Academic Groups by their faculty.

    Because faculties don't have persistent external IDs, they're not stored in the database.
    """

    short_name = models.CharField(max_length=255, unique=True)

    parent: models.ForeignKey[Faculty | None] = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
    )

    def __str__(self) -> str:
        return self.short_name

    class Meta(BaseModel.Meta):
        indexes = [
            models.Index(fields=["uuid", "short_name"]),
            models.Index(fields=["short_name"]),
        ]
