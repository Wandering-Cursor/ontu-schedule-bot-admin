import datetime
from typing import TYPE_CHECKING, TypeVar

from django.utils import timezone
from ontu_parser.classes import Parser
from ontu_schedule_admin.api.utils.log import make_log

if TYPE_CHECKING:
    from zoneinfo import ZoneInfo

    from ontu_parser.classes.dataclasses import Department as ParserDepartment
    from ontu_parser.classes.dataclasses import Faculty as ParserFaculty
    from ontu_parser.classes.dataclasses import Group as ParserGroup
    from ontu_parser.classes.dataclasses import StudentsPair
    from ontu_parser.classes.dataclasses import Teacher as ParseTeacher

    from main.models.group import Group

T = TypeVar("T")

global_parser = Parser()
global_teacher_parser = Parser(kwargs={"for_teachers": True})

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
    "П’ятниця": 4,  # Typographic apostrophe
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
    weekday = today_kyiv.weekday()  # Monday=0 ... Sunday=6
    if weekday == 6:  # Sunday
        return today_kyiv + datetime.timedelta(days=1)
    # Move back to Monday of the same week
    return today_kyiv - datetime.timedelta(days=weekday)


def remap_ukrainian_week_to_dates(schedule_by_dayname: dict[str, T]) -> dict[datetime.date, T]:
    """Remap a dict keyed by Ukrainian weekday names to actual dates for Kyiv.

    - If today (in Kyiv) is not Sunday: map to dates of the current week (Mon–Sat/Sun)
    - If today is Sunday: map to dates of the next week (Mon–Sat/Sun)

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


def get_faculties() -> list[ParserFaculty]:
    faculties = global_parser.get_faculties()
    faculties += global_parser.get_all_extramurals()

    return faculties


def get_faculty_by_name(faculty_name: str) -> ParserFaculty | None:
    faculties = global_parser.get_faculties()
    for faculty in faculties:
        if faculty.get_faculty_name() == faculty_name:
            return faculty
    return None


def get_departments() -> list[ParserDepartment]:
    return global_teacher_parser.get_departments()


def get_group(group: Group) -> ParserGroup | None:
    groups = get_groups(faculty_name=group.faculty.short_name)
    for parser_group in groups:
        if parser_group.get_group_name() == group.short_name:
            return parser_group
    return None


def get_groups(faculty_name: str) -> list[ParserGroup]:
    faculty = get_faculty_by_name(faculty_name)

    if faculty is None:
        make_log(
            {
                "msg": f"Faculty with name {faculty_name} not found",
            },
            level="ERROR",
        )
        return []

    return global_parser.get_groups(
        faculty=faculty,
    )


def get_teachers(department_external_id: str) -> list[ParseTeacher]:
    return global_teacher_parser.get_teachers_by_department(
        department_id=int(department_external_id),
    )


def get_schedule_by_group(
    group: Group,
) -> dict[datetime.date, list[StudentsPair]]:
    api_group = get_group(group)

    if not api_group:
        raise ValueError(
            f"Group {group.short_name} not found in faculty {group.faculty.short_name}"
        )

    result = global_parser.get_schedule(
        group_id=int(api_group.get_group_id()),  # pyright: ignore[reportArgumentType]
    )

    return remap_ukrainian_week_to_dates(result)
