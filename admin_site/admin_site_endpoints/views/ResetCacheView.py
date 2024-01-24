from admin_site_endpoints import operations as endpoint_operations
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


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
