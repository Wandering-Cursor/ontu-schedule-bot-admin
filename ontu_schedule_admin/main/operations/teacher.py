from typing import TYPE_CHECKING

import pydantic
from main.models.department import Department
from main.models.teacher import Teacher

from .third_party.schedule_api import get_teachers

if TYPE_CHECKING:
    import pydantic


async def _process_department(department: Department) -> None:
    api_teachers = await get_teachers(
        department_external_id=department.external_id,
    )

    for api_teacher in api_teachers:
        teacher_names = api_teacher.teacher_name

        teacher, _ = await Teacher.objects.aupdate_or_create(
            external_id=api_teacher.teacher_id,
            defaults={
                "short_name": teacher_names.short,
                "full_name": teacher_names.full,
            },
        )

        department_exists = await teacher.departments.filter(uuid=department.uuid).aexists()
        if not department_exists:
            await teacher.departments.aadd(department)


async def update_teachers_from_api(
    department_ids: list[pydantic.UUID4] | None,
) -> None:
    if department_ids is None:
        departments_qs = Department.objects.all()
    else:
        departments_qs = Department.objects.filter(uuid__in=department_ids)

    departments = [department async for department in departments_qs]

    for department in departments:
        await _process_department(department)


async def read_teacher(teacher_id: pydantic.UUID4) -> Teacher:
    return await Teacher.objects.aget(uuid=teacher_id)
