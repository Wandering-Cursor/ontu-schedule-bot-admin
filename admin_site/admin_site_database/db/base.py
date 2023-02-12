"""Module containing base manager"""
from django.db.models import Manager


class BaseManager(Manager):
    """Base manager that is going to be used everywhere"""
