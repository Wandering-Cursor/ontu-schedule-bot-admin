from admin_site_database.model_files import TelegramChat
from rest_framework import serializers


class TelegramChatSerializer(serializers.ModelSerializer):
    chat_id = serializers.CharField(source="telegram_id")
    chat_name = serializers.CharField(source="name")
    thread_id = serializers.IntegerField(
        source="topic_id",
        required=False,
        allow_null=True,
    )
    chat_info = serializers.CharField()
    is_forum = serializers.BooleanField(default=False)

    class Meta:
        model = TelegramChat
        fields = [
            "chat_id",
            "chat_name",
            "thread_id",
            "chat_info",
            "is_forum",
        ]
