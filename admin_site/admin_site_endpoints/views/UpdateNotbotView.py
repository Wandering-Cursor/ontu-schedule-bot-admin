from admin_site_database import operations
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


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
