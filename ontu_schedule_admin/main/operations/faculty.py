from ontu_schedule_admin.api.utils.log import make_log

from main.models.faculty import Faculty

from .third_party.schedule_api import get_faculties


def update_faculties_from_api() -> None:
    api_faculties = get_faculties()

    make_log(
        {
            "msg": f"Got {len(api_faculties)} faculties from Schedule API",
        },
        level="INFO",
    )

    for api_faculty in api_faculties:
        Faculty.objects.update_or_create(
            short_name=api_faculty.get_faculty_name(),
        )
