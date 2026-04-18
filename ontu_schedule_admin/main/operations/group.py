from typing import TYPE_CHECKING

from main.models.faculty import Faculty
from main.models.group import Group
from ontu_schedule_admin.api.utils.log import main_logger

from .third_party.schedule_api import get_extramural_faculty, get_faculty_by_name, get_groups

if TYPE_CHECKING:
    import pydantic


async def update_groups_from_api(faculty_ids: list[pydantic.UUID4] | None) -> None:
    if faculty_ids is None:
        faculties_qs = Faculty.objects.select_related("parent").all()
    else:
        faculties_qs = Faculty.objects.select_related("parent").filter(uuid__in=faculty_ids)

    faculties = [faculty async for faculty in faculties_qs]

    for faculty in faculties:
        if parent := faculty.parent:
            api_parent_faculty = await get_faculty_by_name(parent.short_name)
            if not api_parent_faculty:
                main_logger.warning(
                    {
                        "msg": "Could not find parent faculty in Schedule API",
                        "parent": parent,
                        "faculty": faculty,
                    }
                )
                continue
            api_faculty = await get_extramural_faculty(faculty=api_parent_faculty)
        else:
            api_faculty = await get_faculty_by_name(faculty.short_name)

        if not api_faculty:
            main_logger.warning(
                {
                    "msg": "Could not find faculty in Schedule API",
                    "faculty": faculty,
                }
            )
            continue

        groups = await get_groups(faculty=api_faculty)

        for group in groups:
            await Group.objects.aupdate_or_create(
                faculty=faculty,
                short_name=group.group_name,
            )


async def read_group(group_id: pydantic.UUID4) -> Group:
    return await Group.objects.select_related("faculty__parent").aget(uuid=group_id)
