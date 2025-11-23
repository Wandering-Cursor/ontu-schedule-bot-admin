from main.models.chat import Chat
from rest_framework import serializers


class ChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chat
        fields = [
            "uuid",
            "platform",
            "platform_chat_id",
            "title",
            "username",
            "first_name",
            "last_name",
            "language_code",
            "additional_info",
        ]
