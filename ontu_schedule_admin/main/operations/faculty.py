from main.models.faculty import Faculty
from ontu_schedule_admin.api.utils.log import make_log

from .third_party.schedule_api import get_faculties, get_faculty_by_id


async def update_faculties_from_api() -> None:
    api_faculties = await get_faculties()

    make_log(
        {
            "msg": f"Got {len(api_faculties)} faculties from Schedule API",
        },
        level="INFO",
    )

    for api_faculty in api_faculties:
        api_parent = None
        if parent_id := api_faculty.parent_id:
            api_parent = await get_faculty_by_id(parent_id)

        parent_faculty = None
        if api_parent:
            parent_faculty = await Faculty.objects.aget(
                short_name=api_parent.faculty_name,
            )

        await Faculty.objects.aupdate_or_create(
            short_name=api_faculty.faculty_name,
            defaults={
                "parent": parent_faculty,
            },
        )
