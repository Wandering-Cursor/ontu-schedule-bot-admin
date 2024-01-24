from admin_site_database import model_files, operations
from django.utils import timezone
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


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
