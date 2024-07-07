from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_site_database import model_files


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
