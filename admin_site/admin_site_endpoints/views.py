from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.request import Request

from admin_site_database import models

from admin_site_database import operations


class BaseAPIView(APIView):
    """Base View for API"""

# region Chat Views

class ChatInfoView(BaseAPIView):
    def post(self, request: Request):
        request_data: dict[str, object] = request.data
        telegram_chat = models.TelegramChat.objects.filter(
            telegram_id=request_data['chat_id']
        ).first()
        if isinstance(telegram_chat, models.TelegramChat):
            return Response(
                data={
                    "status": "ok",
                    **telegram_chat.as_json(),
                },
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
        return Response(
            data={
                "status": "ok",
                **chat.as_json()
            }
        )


class ChatsAllView(BaseAPIView):
    def post(self, request):
        result = []
        for chat in models.TelegramChat.objects.all():
            chat: models.TelegramChat
            result.append(
                chat.as_json()
            )
        return Response(
            data=result
        )


class ChatUpdateView(BaseAPIView):
    def post(self, request: Request):
        request_data = request.data

        telegram_id = request_data["chat_id"]
        group_info = request_data["group"]
        is_active = request_data["is_active"]

        telegram_chat: models.TelegramChat = models.TelegramChat.objects.filter(
            telegram_id=telegram_id
        ).first()
        if not telegram_chat:
            return Response(status=404)

        group = models.Group.objects.filter(
            name=group_info["name"],
            faculty__name=group_info["faculty"]
        ).first()
        if not group:
            return Response(status=404)

        subscription, _ = models.Subscription.objects.update_or_create(
            is_active=is_active,
            group=group
        )
        subscription: models.Subscription
        telegram_chat.subscription = subscription
        subscription.save()
        telegram_chat.save()
        return Response(
            data={
                "status": "ok",
                **subscription.as_json()
            }
        )

# endregion

# region ONTU stuff Views
class FacultiesGetView(APIView):
    def post(self, response):
        result = []
        for faculty in models.Faculty.objects.all():
            faculty: models.Faculty
            result.append(
                faculty.as_json()
            )
        return Response(
            data=result
        )


class GroupsGetView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        result = []
        for group in models.Group.objects.filter(
            faculty__name=request_data['faculty_name']
        ).all():
            group: models.Group
            result.append(
                group.as_json()
            )
        return Response(
            data=result
        )
# endregion

class ScheduleGetView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        group_name = request_data['group']
        faculty_name = request_data['faculty']

        group: models.Group | None = models.Group.objects.filter(
            name=group_name,
            faculty__name=faculty_name
        ).first()
        if not group:
            return Response(status=404)

        schedule = operations.fetch_schedule(
            faculty_name=group.faculty.name,
            group_name=group.name
        )
        return Response(
            data=schedule
        )
