"""
Base Model
"""
import uuid

from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    """Base model for all the others. Contains some common params"""
    id = models.UUIDField(primary_key=True)
    created = models.DateTimeField()
    updated = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = uuid.uuid4()
        if not self.created:
            self.created = timezone.now()
        self.updated = timezone.now()
        super().save(*args, **kwargs)

    def as_json(self):
        """
        This method is used to represent objects as JSON for responses
        """
        raise NotImplementedError("You have to impellent as_json for", self)

    class Meta:
        """
        This is an abstract class, since it's the base class
        """
        abstract = True
