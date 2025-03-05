"""
Imports of models for database ops
"""

from .base import BaseModel
from .department import Department
from .faculty import Faculty
from .group import Group
from .message_campaign import MessageCampaign
from .settings import Settings
from .subscription import Subscription
from .teacher import Teacher
from .teachers_schedule_cache import TeacherScheduleCache
from .telegram_chat import TelegramChat

__all__ = [
    "BaseModel",
    "Department",
    "Faculty",
    "Group",
    "MessageCampaign",
    "Settings",
    "Subscription",
    "Teacher",
    "TelegramChat",
    "TeacherScheduleCache",
]
