import logging

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_site_database import model_files, operations
from admin_site_endpoints.views.ScheduleGetView import ScheduleGetView
from admin_site_endpoints.views.TeachersScheduleView import TeachersScheduleView


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
                        "chat_info": [
                            {
                                "chat_id": chat.telegram_id,
                                "topic_id": chat.topic_id,
                            }
                            for chat in subscription.related_telegram_chats
                        ],
                    }
                )

        return Response(data=result)
