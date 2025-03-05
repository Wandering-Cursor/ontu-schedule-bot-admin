from admin_site_database.model_files import TelegramChat
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from admin_site_endpoints.serializers.chat import TelegramChatSerializer


class ChatCreateView(GenericAPIView):
    @extend_schema(
        request=TelegramChatSerializer,
        responses={
            201: TelegramChatSerializer,
        },
    )
    def post(self, request: Request) -> Response:
        """
        Create a new chat from with some information from a Telegram Bot

        NOTE: The serializer is spreading lies, since the response has a different format at the moment
        """  # noqa: E501
        serializer = TelegramChatSerializer(data=request.data)

        if serializer.is_valid():
            chat, created = TelegramChat.objects.get_or_create(
                telegram_id=serializer.validated_data["telegram_id"],
                name=serializer.validated_data["name"],
                topic_id=serializer.validated_data["topic_id"],
                defaults={
                    "chat_info": serializer.validated_data["chat_info"],
                    "is_forum": serializer.validated_data["is_forum"],
                },
            )
            if created:
                chat.save()

            return Response(data={"status": "ok", **chat.as_json()}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
