# region Chat Views


from rest_framework.request import Request
from rest_framework.response import Response

from admin_site_database import model_files
from admin_site_endpoints.views.BaseAPIView import BaseAPIView


class ChatInfoView(BaseAPIView):
    def post(self, request: Request):
        request_data: dict[str, object] = request.data
        telegram_chat = model_files.TelegramChat.objects.filter(
            telegram_id=request_data["chat_id"],
            topic_id=request_data["topic_id"],
        ).first()

        if isinstance(telegram_chat, model_files.TelegramChat):
            return Response(
                data={
                    "status": "ok",
                    **telegram_chat.as_json(),
                },
                status=200,
            )
        else:
            return Response(status=404)
