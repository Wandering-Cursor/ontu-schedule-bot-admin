import datetime
from typing import TYPE_CHECKING

from django.core.cache import cache
from ontu_schedule_admin.api.schemas.schedule import (
    DaySchedule,
    Lesson,
    Pair,
    Teacher,
    WeekSchedule,
)
from ontu_schedule_admin.api.utils.log import make_log

if TYPE_CHECKING:
    from main.models.group import Group

from main.operations.third_party.schedule_api import (
    get_schedule_by_group as api_get_schedule_by_group,
)


def get_week_schedule_by_group(
    group: Group,
    ignore_cache: bool = False,
) -> WeekSchedule:
    key = f"{group.uuid}_schedule"

    cached_schedule = cache.get(key)
    if cached_schedule is not None and not ignore_cache:
        make_log(
            {
                "msg": f"Schedule for group {group.short_name} fetched from cache",
            },
            level="INFO",
        )
        return cached_schedule

    api_schedule = api_get_schedule_by_group(group=group)

    schedule = WeekSchedule(days=[])

    for date, pairs in api_schedule.items():
        schedule.days.append(
            DaySchedule(
                date=date,
                pairs=[
                    Pair(
                        number=pair.pair_no,
                        lessons=[
                            Lesson(
                                short_name=lesson.lesson_name["short"],
                                full_name=lesson.lesson_name["full"],
                                teacher=Teacher(
                                    short_name=lesson.teacher["short"],
                                    full_name=lesson.teacher["full"],
                                ),
                                card=lesson.lesson_info,
                                auditorium=lesson.auditorium,
                            )
                            for lesson in pair.lessons
                        ],
                    )
                    for pair in pairs
                ],
            )
        )

    cache.set(
        key,
        schedule,
        timeout=60 * 30,
    )

    make_log(
        {
            "msg": f"Schedule for group {group.short_name} cached",
        },
        level="INFO",
    )

    return schedule


def get_day_schedule_by_group(
    group: Group,
    for_day: datetime.date,
    ignore_cache: bool = False,
) -> DaySchedule | None:
    full_schedule = get_week_schedule_by_group(
        group=group,
        ignore_cache=ignore_cache,
    )

    for day in full_schedule.days:
        if day.date == for_day:
            return day

    return None
