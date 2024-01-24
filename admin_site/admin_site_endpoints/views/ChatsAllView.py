from admin_site_database import model_files
from admin_site_endpoints.views.BaseAPIView import BaseAPIView
from rest_framework.response import Response


class ChatsAllView(BaseAPIView):
    def post(self, request):
        result = []
        for chat in model_files.TelegramChat.objects.all():
            chat: model_files.TelegramChat
            result.append(chat.as_json())
        return Response(data=result)
