import logging
from typing import TYPE_CHECKING

from admin_site_database import model_files, operations
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from admin_site_endpoints.serializers.schedule import BatchScheduleSerializer
from admin_site_endpoints.views.ScheduleGetView import ScheduleGetView
from admin_site_endpoints.views.TeachersScheduleView import TeachersScheduleView

if TYPE_CHECKING:
    from django.db.models.manager import BaseManager


class BatchScheduleView(GenericAPIView):
    @extend_schema(
        responses={
            200: [BatchScheduleSerializer],
        }
    )
    def get(
        self,
        request: Request,  # noqa: ARG002
    ) -> Response:
        """
        Get a list of schedules for all active subscriptions.

        WARNING: May take a long time to process if there are many subscriptions.
        For 400 or so subs - it takes about 100 seconds to process, but may depend on how many are
        currntly active.
        """
        result = []

        active_subscriptions = self.get_active_subscriptions()
        groups_per_faculty = self.get_groups_per_faculty()

        for subscription in active_subscriptions.all():
            if not subscription.related_telegram_chats:
                continue

            if subscription.group:
                self.process_group_subscription(subscription, groups_per_faculty, result)
            elif subscription.teacher:
                self.process_teacher_subscription(subscription, result)

        return Response(data=result)

    def get_active_subscriptions(self) -> "BaseManager[model_files.Subscription]":
        """Returns a manager of active subscriptions"""
        return model_files.Subscription.objects.filter(
            is_active=True,
        ).all()

    def get_groups_per_faculty(self) -> dict[str, dict[str, int]]:
        """
        Returns a dictionary of groups per faculty
        With their names as keys and dictionaries of group names and ids as values

        IDs are used for fetching schedules
        """
        groups_per_faculty_tmp = operations.fetch_groups(
            faculty_entities=list(model_files.Faculty.objects.all())
        )

        groups_per_faculty = {}
        for faculty, groups in groups_per_faculty_tmp.items():
            new_groups = {group.get_group_name(): int(group.get_group_id()) for group in groups}
            groups_per_faculty[faculty.name] = new_groups

        return groups_per_faculty

    def process_group_subscription(
        self,
        subscription: "model_files.Subscription",
        groups_per_faculty: dict[str, dict[str, int]],
        result: list,
    ) -> None:
        """
        Adding a group to the list of results

        NOTE: Using inplace operations to avoid creating new objects
        """
        faculty = subscription.group.faculty
        group = subscription.group

        group_id = groups_per_faculty[faculty.name].get(group.name, None)
        if group_id is None:
            logging.warning(f"Group {group.name} not found in {faculty.name}")
            return

        result.append(
            {
                "faculty_name": faculty.name,
                "group_name": group.name,
                "schedule": ScheduleGetView.get_schedule_for_batch(
                    group=group,
                    group_id=group_id,
                ),
                "chat_info": self.get_chat_info(subscription),
            }
        )

    def process_teacher_subscription(
        self,
        subscription: model_files.Subscription,
        result: list,
    ) -> None:
        """
        Adding a teacher to the list of results

        NOTE: Using inplace operations to avoid creating new objects
        """
        result.append(
            {
                "department": subscription.teacher.department.short_name,
                "teacher": subscription.teacher.full_name,
                "schedule": TeachersScheduleView.get_schedule(teacher=subscription.teacher),
                "chat_info": self.get_chat_info(subscription),
            }
        )

    def get_chat_info(self, subscription: model_files.Subscription) -> list[dict[str, int]]:
        """
        Returns a list of chat info dictionaries for a subscription
        """
        return [
            {
                "chat_id": chat.telegram_id,
                "topic_id": chat.topic_id,
            }
            for chat in subscription.related_telegram_chats
        ]
