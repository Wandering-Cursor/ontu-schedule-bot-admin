import datetime
from typing import TYPE_CHECKING, TypeVar
from zoneinfo import ZoneInfo

from django.db.models import aprefetch_related_objects
from django.utils import timezone
from main.operations.third_party.decorator import catch_api_exception
from main.operations.third_party.errors import FacultyNotFoundError, GroupNotFoundError
from ontu_parser.dataclasses.sender import SenderOptions
from ontu_parser.parser import AsyncParser
from ontu_schedule_admin.api.utils.log import make_log

if TYPE_CHECKING:
    from main.models.group import Group
    from main.models.teacher import Teacher
    from ontu_parser.dataclasses import Department as ParserDepartment
    from ontu_parser.dataclasses import Faculty as ParserFaculty
    from ontu_parser.dataclasses import Group as ParserGroup
    from ontu_parser.dataclasses import StudentsPair, TeachersPair
    from ontu_parser.dataclasses import Teacher as ParseTeacher

T = TypeVar("T")

async_global_parser = AsyncParser()
async_global_teacher_parser = AsyncParser(SenderOptions(for_teachers=True))

try:
    KYIV_TZ = ZoneInfo("Europe/Kyiv")
except Exception:  # noqa: BLE001
    KYIV_TZ = None  # type: ignore


# Ukrainian day-name to weekday offset mapping (Monday=0 ... Sunday=6)
UA_DAY_TO_OFFSET: dict[str, int] = {
    "Понеділок": 0,
    "Вівторок": 1,
    "Середа": 2,
    "Четвер": 3,
    "П'ятниця": 4,  # ASCII apostrophe
    "П’ятниця": 4,  # Typographic apostrophe  # noqa: RUF001
    "П`ятниця": 4,  # Backtick variant (observed in source)
    "Субота": 5,
    "Неділя": 6,
}


def _kyiv_now() -> datetime.datetime:
    """
    Return current time in Kyiv timezone as an aware datetime.

    We prefer the IANA tz 'Europe/Kyiv' via zoneinfo to avoid dependency on
    Django settings for correct local week computations.
    """
    now_utc = datetime.datetime.now(datetime.UTC)

    if KYIV_TZ is not None:
        return now_utc.astimezone(KYIV_TZ)

    return timezone.localtime(now_utc)


def _monday_of_relevant_week(today_kyiv: datetime.date) -> datetime.date:
    """Compute the Monday date for the current or next week in Kyiv.

    Rule:
    - If today is Sunday in Kyiv -> use next week's Monday
    - Otherwise -> use Monday of this week
    """
    sunday_index = 6

    weekday = today_kyiv.weekday()

    if weekday == sunday_index:  # Sunday
        return today_kyiv + datetime.timedelta(days=1)
    # Move back to Monday of the same week
    return today_kyiv - datetime.timedelta(days=weekday)


def remap_ukrainian_week_to_dates(schedule_by_dayname: dict[str, T]) -> dict[datetime.date, T]:  # noqa: UP047
    """Remap a dict keyed by Ukrainian weekday names to actual dates for Kyiv.

    - If today (in Kyiv) is not Sunday: map to dates of the current week (Mon-Sat/Sun)
    - If today is Sunday: map to dates of the next week (Mon-Sat/Sun)

    Unknown keys are ignored.
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # type: ignore
    # If keys are already dates, return as-is
    """
    now_kyiv = _kyiv_now()
    base_monday = _monday_of_relevant_week(now_kyiv.date())

    remapped: dict[datetime.date, T] = {}

    for name, offset in UA_DAY_TO_OFFSET.items():
        if name in schedule_by_dayname:
            target_date = base_monday + datetime.timedelta(days=offset)
            remapped[target_date] = schedule_by_dayname[name]

    return remapped


@catch_api_exception
async def get_faculties() -> list[ParserFaculty]:
    faculties = await async_global_parser.get_faculties()
    faculties += await async_global_parser.get_all_extramurals()

    return faculties


@catch_api_exception
async def get_faculty_by_id(faculty_id: int) -> ParserFaculty | None:
    """
    !IMPORTANT!
    !This method can only work within the same PHP Session!
    """
    return await async_global_parser.get_faculty(faculty_id=faculty_id)


@catch_api_exception
async def get_faculty_by_name(faculty_name: str) -> ParserFaculty | None:
    faculties = await async_global_parser.get_faculties()
    for faculty in faculties:
        if faculty.faculty_name == faculty_name:
            return faculty
    return None


@catch_api_exception
async def get_extramural_faculty(faculty: ParserFaculty) -> ParserFaculty | None:
    return await async_global_parser.get_extramural(faculty=faculty)


@catch_api_exception
async def get_departments() -> list[ParserDepartment]:
    return await async_global_teacher_parser.get_departments()


@catch_api_exception
async def get_group(group: Group) -> ParserGroup | None:
    await aprefetch_related_objects([group], "faculty__parent")
    faculty = group.faculty

    if parent := faculty.parent:
        api_parent_faculty = await get_faculty_by_name(parent.short_name)
        if not api_parent_faculty:
            make_log(
                {
                    "msg": "Could not find parent faculty in Schedule API",
                    "parent": parent,
                    "faculty": faculty,
                },
                level="WARNING",
            )
            return None

        api_faculty = await get_extramural_faculty(faculty=api_parent_faculty)
    else:
        api_faculty = await get_faculty_by_name(faculty.short_name)

    if not api_faculty:
        make_log(
            {
                "msg": "Could not find faculty in Schedule API",
                "faculty": faculty,
            },
            level="WARNING",
        )
        return None

    groups = await get_groups(faculty=api_faculty)

    for parser_group in groups:
        if parser_group.group_name == group.short_name:
            return parser_group

    return None


@catch_api_exception
async def get_groups(
    faculty_name: str | None = None,
    faculty: ParserFaculty | None = None,
) -> list[ParserGroup]:
    xor = (faculty_name is None) != (faculty is None)
    if not xor:
        raise ValueError("Exactly one of faculty_name or faculty must be provided")

    if faculty is None and faculty_name is not None:
        faculty = await get_faculty_by_name(faculty_name)

    if faculty is None:
        make_log(
            {
                "msg": f"Faculty with name {faculty_name} not found",
            },
            level="ERROR",
        )
        raise FacultyNotFoundError(f"Faculty with name {faculty_name} not found")

    return await async_global_parser.get_groups(
        faculty=faculty,
    )


@catch_api_exception
async def get_teachers(department_external_id: str) -> list[ParseTeacher]:
    return await async_global_teacher_parser.get_teachers_by_department(
        department_id=int(department_external_id),
    )


@catch_api_exception
async def get_student_schedule_by_group(
    group: Group,
) -> dict[datetime.date, list[StudentsPair]]:
    group = await group.__class__.objects.select_related("faculty").aget(pk=group.pk)
    api_group = await get_group(group)

    if not api_group:
        raise GroupNotFoundError(
            f"Group {group.short_name} not found in faculty {group.faculty.short_name}"
        )

    result = await async_global_parser.get_schedule(
        group_id=int(api_group.group_id),
    )

    return remap_ukrainian_week_to_dates(result)  # pyright: ignore[reportReturnType]


@catch_api_exception
async def get_teacher_schedule_by_teacher(
    teacher: Teacher,
) -> dict[datetime.date, list[TeachersPair]]:
    result = await async_global_teacher_parser.get_schedule(
        teacher_id=int(teacher.external_id),  # pyright: ignore[reportArgumentType]
    )

    return remap_ukrainian_week_to_dates(result)  # pyright: ignore[reportReturnType]
