from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_site_database import operations


class UpdateNotbotView(APIView):
    def get(self, _: Request):
        try:
            global_value = operations.global_parser.sender.cookies.get_cookie()
            teachers_value = operations.teachers_parser.sender.cookies.get_cookie()
            if global_value and teachers_value:
                return Response(status=200)
            raise ValueError("Expecting cookies to be set")
        except (ValueError, ConnectionError, Exception) as exception:
            return Response(
                data=f"Cookies not set to desired value. {exception}",
                status=500,
            )
