from typing import TYPE_CHECKING

import pydantic
from django.db import transaction

from main.models.department import Department
from main.models.teacher import Teacher

from .third_party.schedule_api import get_teachers

if TYPE_CHECKING:
    import pydantic


@transaction.atomic
def _process_department(department: Department) -> None:
    api_teachers = get_teachers(
        department_external_id=department.external_id,
    )

    for api_teacher in api_teachers:
        teacher_names = api_teacher.get_teacher_name()

        teacher, _ = Teacher.objects.update_or_create(
            external_id=api_teacher.get_teacher_id(),
            defaults={
                "short_name": teacher_names["short"],
                "full_name": teacher_names["full"],
            },
        )

        if not teacher.departments.filter(uuid=department.uuid).exists():
            teacher.departments.add(department)
            teacher.save()


def update_teachers_from_api(
    department_ids: list[pydantic.UUID4] | None,
) -> None:
    if department_ids is None:
        departments = Department.objects.all()
    else:
        departments = Department.objects.filter(uuid__in=department_ids)

    for department in departments:
        _process_department(department)
