"""
Settings model
"""

from django.db import models

from admin_site_database import db as admin_db
from admin_site_database.model_files import BaseModel


class Settings(BaseModel):
    """Model for various settings in app"""

    name = models.TextField()

    value = models.TextField()

    objects = admin_db.SettingsManager
