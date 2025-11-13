from django.contrib.auth.models import AbstractBaseUser
from django.db import models

from main.models.base import BaseModel


class APIUser(BaseModel, AbstractBaseUser):
    USERNAME_FIELD = "username"

    username = models.CharField(max_length=255, unique=True)
