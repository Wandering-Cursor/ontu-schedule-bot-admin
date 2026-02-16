from main.models.message_campaign import MessageCampaign
from rest_framework import serializers

from ontu_schedule_admin.api.serializers.chat import ChatSerializer


class MessageCampaignSerializer(serializers.ModelSerializer):
    recipients = ChatSerializer(
        many=True,
        read_only=True,
    )

    def to_representation(self, instance):  # noqa: ANN001, ANN201
        data = super().to_representation(instance)

        if chat_id := self.context.get("X-Chat-ID"):
            data["recipients"] = [
                item for item in data["recipients"] if item["platform_chat_id"] == chat_id
            ]

        return data

    class Meta:
        model = MessageCampaign
        fields = [
            "uuid",
            "name",
            "payload",
            "recipients",
            "created_at",
        ]
