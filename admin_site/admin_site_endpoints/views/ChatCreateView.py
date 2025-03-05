from rest_framework.request import Request
from rest_framework.response import Response

from admin_site_database import model_files
from admin_site_endpoints.views.BaseAPIView import BaseAPIView


class ChatCreateView(BaseAPIView):
    def post(self, request: Request):
        request_data: dict[str, object] = request.data
        chat, created = model_files.TelegramChat.objects.get_or_create(
            telegram_id=request_data["chat_id"],
            name=request_data["chat_name"],
            topic_id=request_data["thread_id"],
            defaults={
                "chat_info": request_data["chat_info"],
                "is_forum": request_data["is_forum"] or False,
            },
        )
        if created:
            chat.save()
        return Response(data={"status": "ok", **chat.as_json()})
