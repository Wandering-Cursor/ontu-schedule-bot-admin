"""Models for endpoints app"""

from django.db import models


class ScheduleCache(models.Model):
    """ScheduleCache model Stores schedule for each group in JSON format"""

    faculty = models.CharField(max_length=100)
    group = models.CharField(max_length=100)
    schedule = models.JSONField(null=True)
    at_time = models.DateTimeField(auto_now=True)
