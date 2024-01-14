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


class ChatCreateView(BaseAPIView):
    def post(self, request: Request):
        request_data: dict[str, object] = request.data
        chat, created = model_files.TelegramChat.objects.get_or_create(
            telegram_id=request_data["chat_id"],
            name=request_data["chat_name"],
            topic_id=request_data["thread_id"],
            defaults={
                "chat_info": request_data["chat_info"],
                "is_forum": request_data["is_forum"],
            },
        )
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
        for group in model_files.Group.objects.filter(
            faculty__name=request_data["faculty_name"],
        ).all():
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
            notbot_value_teachers = (
                operations.teachers_parser.sender.notbot.get_notbot()
            )
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

        _, result = endpoint_operations.reset_cache(
            faculty_name=faculty_name,
            group_name=group_name,
        )
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
    @staticmethod
    def get_cached_schedule(group: model_files.Group):
        cache = ScheduleCache.objects.filter(
            faculty=group.faculty.name,
            group=group.name,
            at_time__gte=timezone.now() - timezone.timedelta(minutes=45),
        )
        logging.error(f"Cache: {cache}")
        if cache.exists():
            return cache.first().schedule

    @staticmethod
    def add_schedule_to_cache(group: model_files.Group, schedule: dict):
        logging.error(f"Schedule: {schedule}")
        entity, _ = ScheduleCache.objects.get_or_create(
            faculty=group.faculty.name,
            group=group.name,
        )
        entity.schedule = schedule
        entity.save()

    @staticmethod
    def get_schedule(group: model_files.Group):
        cached_schedule = ScheduleGetView.get_cached_schedule(group=group)
        if cached_schedule:
            return cached_schedule

        schedule = operations.get_schedule_by_names(
            faculty_name=group.faculty.name,
            group_name=group.name,
        )
        ScheduleGetView.add_schedule_to_cache(group=group, schedule=schedule)
        return schedule

    @staticmethod
    def get_schedule_for_batch(group: model_files.Group, group_id: int):
        cached_schedule = ScheduleGetView.get_cached_schedule(group=group)
        if cached_schedule:
            return cached_schedule

        schedule = operations.get_schedule_by_group_id(group_id=group_id)
        ScheduleGetView.add_schedule_to_cache(group=group, schedule=schedule)
        return schedule

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
        return Response(data=self.get_schedule(group=group))


class TeachersScheduleView(APIView):
    @staticmethod
    def get_schedule(teacher: model_files.Teacher):
        if model_files.TeacherScheduleCache.objects.filter(
            teacher=teacher,
            expires_on__gte=timezone.now(),
        ).exists():
            return model_files.TeacherScheduleCache.objects.get(
                teacher=teacher,
            ).schedule

        schedule = operations.fetch_teacher_schedule(teacher_id=teacher.external_id)
        entity, _ = model_files.TeacherScheduleCache.objects.get_or_create(
            defaults={
                "expires_on": timezone.now() + timezone.timedelta(hours=1),
                "schedule": schedule,
            },
            teacher=teacher,
        )
        entity.save()
        return schedule

    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        teacher_id = request_data["teacher"]

        teacher: model_files.Teacher | None = model_files.Teacher.objects.filter(
            external_id=teacher_id,
        ).first()

        if not teacher:
            return Response(status=404)

        schedule = self.get_schedule(teacher=teacher)
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
        request_data: dict[str, str] = request.GET
        department_id = request_data["department"]
        for teacher in model_files.Teacher.objects.filter(
            department__external_id=department_id,
        ).all():
            teacher: model_files.Teacher
            result.append(teacher.as_json())
        return Response(data=result)

    def put(self, request: Request):
        from ontu_parser.classes.dataclasses import Teacher

        departments: list[int] = []
        department_id = request.data["department"]
        if not department_id:
            departments = [x.external_id for x in model_files.Department.objects.all()]
        else:
            departments = [department_id]
        for department_id in departments:
            teachers: list[Teacher] = operations.get_teachers_by_department(
                department_id=department_id,
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


class BatchScheduleView(APIView):
    def get(self, request: Request):
        result: list[dict[str, str | dict | list[int]]] = []
        active_subscriptions = model_files.Subscription.objects.filter(
            is_active=True
        ).all()
        groups_per_faculty_tmp = operations.fetch_groups(
            faculty_entities=[faculty for faculty in model_files.Faculty.objects.all()]
        )
        groups_per_faculty: dict[str, dict[str, int]] = {}
        for faculty, groups in groups_per_faculty_tmp.items():
            new_groups: dict[str, int] = {}
            for group in groups:
                new_groups[group.get_group_name()] = int(group.get_group_id())
            groups_per_faculty[faculty.name] = new_groups

        for subscription in active_subscriptions:
            subscription: model_files.Subscription
            if not subscription.related_telegram_chats:
                continue

            if subscription.group:
                faculty = subscription.group.faculty
                group = subscription.group

                group_id = groups_per_faculty[faculty.name].get(group.name, None)
                if group_id is None:
                    logging.error(f"Group {group.name} not found in {faculty.name}")
                    continue

                result.append(
                    {
                        "faculty_name": subscription.group.faculty.name,
                        "group_name": subscription.group.name,
                        "schedule": ScheduleGetView.get_schedule_for_batch(
                            group=subscription.group,
                            group_id=group_id,
                        ),
                        "chat_info": [
                            {
                                "chat_id": chat.telegram_id,
                                "topic_id": chat.topic_id,
                            }
                            for chat in subscription.related_telegram_chats
                        ],
                    }
                )
            elif subscription.teacher:
                result.append(
                    {
                        "department": subscription.teacher.department.short_name,
                        "teacher": subscription.teacher.full_name,
                        "schedule": TeachersScheduleView.get_schedule(
                            teacher=subscription.teacher
                        ),
                        "chat_ids": [
                            chat.telegram_id
                            for chat in subscription.related_telegram_chats
                        ],
                    }
                )

        return Response(data=result)
