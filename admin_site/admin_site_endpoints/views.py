from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.request import Request

from admin_site_database import models


class BaseAPIView(APIView):
    """Base View for API"""

class ChatInfoView(BaseAPIView):
    def post(self, request: Request):
        request_data: dict[str, object] = request.data
        telegram_chat = models.TelegramChat.objects.filter(
            telegram_id=request_data['chat_id']
        ).first()
        if isinstance(telegram_chat, models.TelegramChat):
            return Response(
                telegram_chat.as_json(),
                status=200
            )
        else:
            return Response(status=404)


class ChatCreateView(BaseAPIView):
    def post(self, request: Request):
        request_data: dict[str, object] = request.data
        chat, created = models.TelegramChat.objects.get_or_create(
            telegram_id=request_data['chat_id'],
            name=request_data['chat_name'],
            chat_info=request_data['chat_info']
        )
        chat: models.TelegramChat
        if created:
            chat.save()
        return Response(chat.as_json())
