import logging

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from admin_site_database import model_files, operations


class TeachersDepartmentsView(APIView):
    def get(self, _: Request):
        result = []
        for department in model_files.Department.objects.all():
            department: model_files.Department
            result.append(department.as_json())
        return Response(data=result)

    def put(self, _: Request):
        current_departments = operations.get_departments()
        for department in current_departments:
            names = department.get_department_name()
            defaults = {
                "short_name": names["short"],
                "full_name": names["full"],
            }
            entity, created = model_files.Department.objects.update_or_create(
                external_id=department.get_department_id(),
                defaults=defaults,
            )
            logging.warning(f"Department: {entity=} created (or updated): {created=}")
        return Response(status=200)
