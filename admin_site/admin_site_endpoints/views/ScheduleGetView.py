import logging

from django.utils import timezone
from rest_framework.exceptions import APIException
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_site_database import model_files, operations
from admin_site_endpoints.models import ScheduleCache


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
        logging.info(f"Input: {request_data}")

        group: model_files.Group | None = model_files.Group.objects.filter(
            name=group_name, faculty__name=faculty_name
        ).first()
        if not group:
            return Response(status=404)

        logging.info(f"Group: {group}")
        try:
            schedule = self.get_schedule(group=group)
        except Exception as e:
            logging.exception(f"Exception: {e}")
            raise APIException(
                detail=f"Failed to get schedule from ONTU Parser. Error: {e.args}"
            )
        return Response(data=schedule)
