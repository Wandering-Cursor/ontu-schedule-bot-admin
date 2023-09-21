"""Imports for admin_sites"""

from .base import BaseAdmin
from .department import DepartmentAdmin
from .faculty import FacultyAdmin
from .group import GroupAdmin
from .message_campaign import MessageCampaignAdmin
from .subscription import SubscriptionAdmin
from .teacher import TeacherAdmin
from .teachers_schedule_cache import TeacherScheduleCacheAdmin
from .telegram_chat import TelegramChatAdmin

__all__ = [
    "BaseAdmin",
    "DepartmentAdmin",
    "FacultyAdmin",
    "GroupAdmin",
    "MessageCampaignAdmin",
    "SubscriptionAdmin",
    "TeacherAdmin",
    "TeacherScheduleCacheAdmin",
    "TelegramChatAdmin",
]
