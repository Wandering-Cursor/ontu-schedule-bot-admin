from django.db import models
from django.utils import timezone

from .base import BaseModel
from .teacher import Teacher


class TeacherScheduleCache(BaseModel):
    expires_on = models.DateTimeField()
    teacher = models.ForeignKey(
        to=Teacher,
        on_delete=models.CASCADE,
        related_name="schedule_cache",
    )
    schedule = models.JSONField()

    @property
    def department(self):
        return self.teacher.department

    def as_json(self):
        return {
            "expires_on": self.expires_on.isoformat(),
            "teacher": self.teacher.as_json(),
            "schedule": self.schedule,
        }

    def __str__(self) -> str:
        return f"{self.teacher.short_name} schedule cache"

    def clean(self) -> None:
        if not self.expires_on or self.expires_on < timezone.now():
            self.expires_on = timezone.now() + timezone.timedelta(hours=1)
        super().clean()
