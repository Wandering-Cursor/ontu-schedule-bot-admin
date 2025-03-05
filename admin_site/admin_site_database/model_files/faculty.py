"""
Faculty Model
"""

from django.db import models

from admin_site_database import db as admin_db
from admin_site_database.model_files.base import BaseModel


class Faculty(BaseModel):
    """Model for Faculty on Schedule site"""

    name = models.TextField()

    objects = admin_db.FacultyManager()

    def as_json(self):
        return {"name": self.name}

    def __str__(self) -> str:
        return f"Faculty: {self.name}"
