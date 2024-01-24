from admin_site_database import model_files
from rest_framework.response import Response
from rest_framework.views import APIView


class FacultiesGetView(APIView):
    def post(self, response):
        result = []
        for faculty in model_files.Faculty.objects.all():
            faculty: model_files.Faculty
            result.append(faculty.as_json())
        return Response(data=result)
