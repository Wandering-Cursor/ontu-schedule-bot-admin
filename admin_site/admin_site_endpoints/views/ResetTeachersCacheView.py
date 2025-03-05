from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_site_database import model_files


class ResetTeachersCacheView(APIView):
    def post(self, request: Request):
        request_data: dict[str, str] = request.data
        teacher_id = request_data["teacher"]

        _, result = model_files.TeacherScheduleCache.objects.filter(
            teacher__external_id=teacher_id,
        ).delete()
        count: int = list(result.values())[0]

        return Response(status=200, data={"count": count, "status": "ok"})
