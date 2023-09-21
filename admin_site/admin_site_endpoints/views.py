from django.utils import timezone

from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.request import Request

from admin_site_database import model_files

from admin_site_database import operations

from . import operations as endpoint_operations

from .models import ScheduleCache
import logging


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
            operations.teachers_parser.sender.notbot._value = None
            operations.teachers_parser.sender.cookies._value = None
            notbot_value = operations.global_parser.sender.notbot.get_notbot()
            notbot_value_teachers = operations.teachers_parser.sender.notbot.get_notbot()
            if notbot_value and notbot_value_teachers:
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


class ResetTeachersCacheView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        teacher_id = request_data["teacher"]

        _, result = model_files.TeacherScheduleCache.objects.filter(
            teacher__external_id=teacher_id,
        ).delete()
        count: int = list(result.values())[0]

        return Response(status=200, data={"count": count, "status": "ok"})


# endregion


class ScheduleGetView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        group_name = request_data["group"]
        faculty_name = request_data["faculty"]
        logging.error(f"Input: {request_data}")

        group: model_files.Group | None = model_files.Group.objects.filter(
            name=group_name, faculty__name=faculty_name
        ).first()
        if not group:
            return Response(status=404)

        logging.error(f"Group: {group}")
        cache = ScheduleCache.objects.filter(
            faculty=faculty_name,
            group=group_name,
            at_time__gte=timezone.now() - timezone.timedelta(minutes=45),
        )
        logging.error(f"Cache: {cache}")
        if cache.exists():
            return Response(data=cache.first().schedule)

        schedule = operations.fetch_schedule(faculty_name=group.faculty.name, group_name=group.name)
        logging.error(f"Schedule: {schedule}")
        entity, _ = ScheduleCache.objects.get_or_create(faculty=faculty_name, group=group_name)
        entity.schedule = schedule
        entity.save()

        return Response(data=schedule)


class TeachersScheduleView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        teacher_id = request_data["teacher"]

        teacher: model_files.Teacher | None = model_files.Teacher.objects.filter(external_id=teacher_id).first()

        if not teacher:
            return Response(status=404)

        if model_files.TeacherScheduleCache.objects.filter(
            teacher=teacher,
            expires_on__gte=timezone.now(),
        ).exists():
            return Response(
                data=model_files.TeacherScheduleCache.objects.get(
                    teacher=teacher,
                ).schedule
            )

        schedule = operations.fetch_teacher_schedule(teacher_id=teacher_id)
        entity, _ = model_files.TeacherScheduleCache.objects.get_or_create(teacher=teacher)
        entity.schedule = schedule
        entity.save()
        return Response(data=schedule)


class TeachersDepartmentsView(APIView):
    def get(self, _: Request):
        result = []
        for department in model_files.Department.objects.all():
            department: model_files.Department
            result.append(department.as_json())
        return Response(data=result)

    def put(self, _: Request):
        current_departments = operations.get_departments()
        for department in current_departments:
            names = department.get_department_name()
            defaults = {
                "short_name": names["short"],
                "full_name": names["full"],
            }
            entity, created = model_files.Department.objects.update_or_create(
                external_id=department.get_department_id(),
                defaults=defaults,
            )
            logging.warning(f"Department: {entity=} created (or updated): {created=}")
        return Response(status=200)


class TeachersDepartmentView(APIView):
    def get(self, request: Request):
        result = []
        request_data: dict[str, str] = request.data
        department_id = request_data["department"]
        for teacher in model_files.Teacher.objects.filter(
            department_id=department_id,
        ).all():
            teacher: model_files.Teacher
            result.append(teacher.as_json())
        return Response(data=result)

    def put(self, request: Request):
        from ontu_parser.classes.dataclasses import Teacher

        department_id = request.data["department"]
        teachers: list[Teacher] = operations.get_teachers_by_department(
            department=department_id,
        )
        for teacher in teachers:
            names = teacher.get_teacher_name()
            defaults = {
                "short_name": names["short"],
                "full_name": names["full"],
                "department": model_files.Department.objects.filter(
                    external_id=department_id,
                ).first(),
            }
            entity, created = model_files.Teacher.objects.update_or_create(
                external_id=teacher.get_teacher_id(),
                defaults=defaults,
            )
            logging.warning(f"Teacher: {entity=} created (or updated): {created=}")
        return Response(status=200)
