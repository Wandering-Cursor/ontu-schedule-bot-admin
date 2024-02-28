import logging

from admin_site_database import model_files, operations
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from ontu_parser.classes.dataclasses import Teacher


class TeachersDepartmentView(APIView):
    def get(self, request: Request):
        result = []
        request_data: dict[str, str | None] = request.GET
        department_id = request_data.get("department")

        if not department_id or not department_id.isdigit():
            return Response(
                data={"error": "Please, provide `department` query parameter (int)"},
                status=400,
            )

        for teacher in model_files.Teacher.objects.filter(
            departments__external_id=department_id,
        ).all():
            teacher: model_files.Teacher
            result.append(teacher.as_json())
        return Response(data=result)

    def put(self, request: Request):
        departments: list[int] = []
        department_id = request.data.get("department")
        if not department_id:
            departments = [x.external_id for x in model_files.Department.objects.all()]
        else:
            departments = [department_id]
        for department_id in departments:
            teachers: list[Teacher] = operations.get_teachers_by_department(
                department_id=department_id,
            )
            for teacher in teachers:
                names = teacher.get_teacher_name()
                defaults = {
                    "short_name": names["short"],
                    "full_name": names["full"],
                    "department": model_files.Department.objects.filter(
                        external_id=department_id,
                    ).first(),
                }
                entity, created = model_files.Teacher.objects.update_or_create(
                    external_id=teacher.get_teacher_id(),
                    defaults=defaults,
                )

                if defaults["department"] not in entity.departments.all():
                    entity.departments.add(defaults["department"])
                    entity.save()

                logging.warning(f"Teacher: {entity=} created (or updated): {created=}")
        return Response(status=200)
