from rest_framework.request import Request
from rest_framework.response import Response

from admin_site_database import model_files
from admin_site_endpoints.views.BaseAPIView import BaseAPIView


class ChatUpdateView(BaseAPIView):
    def _get_group(self, group_info: dict[str, str]) -> model_files.Group | None:
        group = model_files.Group.objects.filter(
            name=group_info["name"],
            faculty__name=group_info["faculty"],
        ).first()
        if not group:
            return None
        return group

    def _get_teacher(self, teacher_info: dict[str, str]) -> model_files.Teacher | None:
        teacher = model_files.Teacher.objects.filter(
            external_id=teacher_info["external_id"],
        ).first()
        if not teacher:
            return None
        return teacher

    def post(self, request: Request):
        request_data = request.data

        telegram_id = request_data["chat_id"]
        topic_id = request_data["topic_id"]
        group_info = request_data.get("group", None)
        teacher_info = request_data.get("teacher", None)
        is_active = request_data["is_active"]

        telegram_chat: model_files.TelegramChat = (
            model_files.TelegramChat.objects.filter(
                telegram_id=telegram_id,
                topic_id=topic_id,
            ).first()
        )
        if not telegram_chat:
            return Response(status=404)

        if not group_info and not teacher_info:
            return Response(status=400)

        group = None
        teacher = None
        if group_info:
            group = self._get_group(group_info)
            if not group:
                return Response(status=404)

        if teacher_info:
            teacher = self._get_teacher(teacher_info)
            if not teacher:
                return Response(status=404)

        subscription, _ = model_files.Subscription.objects.update_or_create(
            is_active=is_active,
            group=group,
            teacher=teacher,
        )
        subscription: model_files.Subscription
        telegram_chat.subscription = subscription
        subscription.save()
        telegram_chat.save()
        model_files.Subscription.objects.filter(telegram_chats=None).delete()

        return Response(data={"status": "ok", **subscription.as_json()})
