from django.utils import timezone

from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.request import Request

from admin_site_database import model_files

from admin_site_database import operations

from . import operations as endpoint_operations

from .models import ScheduleCache


class BaseAPIView(APIView):
    """Base View for API"""


# region Chat Views


class ChatInfoView(BaseAPIView):
    def post(self, request: Request):
        request_data: dict[str, object] = request.data
        telegram_chat = model_files.TelegramChat.objects.filter(telegram_id=request_data["chat_id"]).first()
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


class ChatCreateView(BaseAPIView):
    def post(self, request: Request):
        request_data: dict[str, object] = request.data
        chat, created = model_files.TelegramChat.objects.get_or_create(
            telegram_id=request_data["chat_id"], name=request_data["chat_name"], chat_info=request_data["chat_info"]
        )
        chat: model_files.TelegramChat
        if created:
            chat.save()
        return Response(data={"status": "ok", **chat.as_json()})


class ChatsAllView(BaseAPIView):
    def post(self, request):
        result = []
        for chat in model_files.TelegramChat.objects.all():
            chat: model_files.TelegramChat
            result.append(chat.as_json())
        return Response(data=result)


class ChatUpdateView(BaseAPIView):
    def post(self, request: Request):
        request_data = request.data

        telegram_id = request_data["chat_id"]
        group_info = request_data["group"]
        is_active = request_data["is_active"]

        telegram_chat: model_files.TelegramChat = model_files.TelegramChat.objects.filter(
            telegram_id=telegram_id
        ).first()
        if not telegram_chat:
            return Response(status=404)

        group = model_files.Group.objects.filter(name=group_info["name"], faculty__name=group_info["faculty"]).first()
        if not group:
            return Response(status=404)

        subscription, _ = model_files.Subscription.objects.update_or_create(is_active=is_active, group=group)
        subscription: model_files.Subscription
        telegram_chat.subscription = subscription
        subscription.save()
        telegram_chat.save()
        return Response(data={"status": "ok", **subscription.as_json()})


# endregion


# region ONTU stuff Views
class FacultiesGetView(APIView):
    def post(self, response):
        result = []
        for faculty in model_files.Faculty.objects.all():
            faculty: model_files.Faculty
            result.append(faculty.as_json())
        return Response(data=result)


class GroupsGetView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        result = []
        for group in model_files.Group.objects.filter(faculty__name=request_data["faculty_name"]).all():
            group: model_files.Group
            result.append(group.as_json())
        return Response(data=result)


class UpdateNotbotView(APIView):
    def get(self, _: Request):
        try:
            operations.global_parser.sender.notbot._value = None
            operations.global_parser.sender.cookies._value = None
            notbot_value = operations.global_parser.sender.notbot.get_notbot()
            if notbot_value:
                return Response(status=200)
            raise ValueError("Expecting notbot_value to be set")
        except (ValueError, ConnectionError, Exception) as exception:
            return Response(
                data=f"Notbot not set to desired value. {exception}",
                status=500,
            )


class ResetCacheView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        group_name = request_data["group"]
        faculty_name = request_data["faculty"]

        _, result = endpoint_operations.reset_cache(faculty_name=faculty_name, group_name=group_name)
        count: int = list(result.values())[0]

        return Response(status=200, data={"count": count, "status": "ok"})


# endregion


class ScheduleGetView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        group_name = request_data["group"]
        faculty_name = request_data["faculty"]

        group: model_files.Group | None = model_files.Group.objects.filter(
            name=group_name, faculty__name=faculty_name
        ).first()
        if not group:
            return Response(status=404)

        cache = ScheduleCache.objects.filter(
            faculty=faculty_name,
            group=group_name,
            at_time__gte=timezone.now() - timezone.timedelta(minutes=45),
        )
        if cache.exists():
            return Response(data=cache.first().schedule)

        schedule = operations.fetch_schedule(faculty_name=group.faculty.name, group_name=group.name)
        entity, _ = ScheduleCache.objects.get_or_create(faculty=faculty_name, group=group_name)
        entity.schedule = schedule
        entity.save()

        return Response(data=schedule)
