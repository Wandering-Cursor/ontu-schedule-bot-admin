from typing import TYPE_CHECKING

from django.db import transaction

from main.models.faculty import Faculty
from main.models.group import Group

from .third_party.schedule_api import get_groups

if TYPE_CHECKING:
    import pydantic


def update_groups_from_api(faculty_ids: list[pydantic.UUID4] | None) -> None:
    if faculty_ids is None:
        faculties = Faculty.objects.all()
    else:
        faculties = Faculty.objects.filter(uuid__in=faculty_ids)

    for faculty in faculties:
        with transaction.atomic():
            groups = get_groups(faculty_name=faculty.short_name)

            for group in groups:
                Group.objects.update_or_create(
                    faculty=faculty,
                    short_name=group.get_group_name(),
                )


def read_group(group_id: pydantic.UUID4) -> Group:
    return Group.objects.get(uuid=group_id)
