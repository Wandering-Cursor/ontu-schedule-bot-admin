"""Imports for admin_sites"""

from .base import BaseAdmin
from .faculty import FacultyAdmin
from .group import GroupAdmin
from .message_campaign import MessageCampaignAdmin
from .subscription import SubscriptionAdmin
from .telegram_chat import TelegramChatAdmin

__all__ = [
    'BaseAdmin',
    'FacultyAdmin',
    'GroupAdmin',
    'MessageCampaignAdmin',
    'SubscriptionAdmin',
    'TelegramChatAdmin',
]
