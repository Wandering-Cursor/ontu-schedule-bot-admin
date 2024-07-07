"""
Group Model
"""

from django.db import models

from admin_site_database import db as admin_db
from admin_site_database.model_files.base import BaseModel
from admin_site_database.model_files.faculty import Faculty


class Group(BaseModel):
    """Model for Group on Schedule site, Group is located inside a Faculty"""

    name = models.TextField()
    faculty = models.ForeignKey(
        to=Faculty, on_delete=models.CASCADE, related_name="groups"
    )

    def as_json(self):
        # I'm not sure how to handle this properly :|
        self.faculty: Faculty
        return {"name": self.name, "faculty": self.faculty.as_json()}

    objects = admin_db.GroupManager

    def __str__(self) -> str:
        return f"Group: {self.name} - {self.faculty}"
