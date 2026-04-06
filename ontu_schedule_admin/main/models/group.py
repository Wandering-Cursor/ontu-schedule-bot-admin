from typing import TYPE_CHECKING

from django.db import models
from main.models.schedule_entity import AbstractScheduleEntity

if TYPE_CHECKING:
    from main.models.faculty import Faculty


class Group(AbstractScheduleEntity):
    """
    Academic Groups represent student cohorts or classes within the institution.

    Because groups don't have persistent external IDs, they're not stored in the database.
    """

    short_name = models.CharField(max_length=255)

    faculty: models.ForeignKey[Faculty] = models.ForeignKey(
        "Faculty",
        on_delete=models.CASCADE,
        related_name="groups",
    )

    def __str__(self) -> str:
        return f"{self.short_name} ({self.faculty!s})"

    class Meta(AbstractScheduleEntity.Meta):
        indexes = [
            models.Index(fields=["uuid", "short_name"]),
            models.Index(fields=["short_name"]),
        ]
        unique_together = [
            ("short_name", "faculty"),
        ]
