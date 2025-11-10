import datetime
from datetime import timedelta

import pydantic  # noqa: TC002
from django.http import HttpRequest  # noqa: TC002
from django.utils import timezone
from main.operations.group import read_group
from main.operations.schedule import get_day_schedule, get_week_schedule
from main.operations.teacher import read_teacher
from ninja import Router
from ninja.errors import HttpError

from ontu_schedule_admin.api.schemas.schedule import DaySchedule, WeekSchedule

from .router import public_router

schedule_router = Router(
    tags=(public_router.tags or [])
    + [
        "Schedule",
    ],
)

student_schedule_router = Router(
    tags=(schedule_router.tags or [])
    + [
        "Student",
    ],
)
teacher_schedule_router = Router(
    tags=(schedule_router.tags or [])
    + [
        "Teacher",
    ],
)


@student_schedule_router.get(
    "/{group_id}",
    response=WeekSchedule,
)
def get_schedule(
    request: HttpRequest,  # noqa: ARG001
    group_id: pydantic.UUID4,
    ignore_cache: bool = False,
) -> WeekSchedule:
    group = read_group(group_id=group_id)

    return get_week_schedule(
        group=group,
        ignore_cache=ignore_cache,
    )


@student_schedule_router.get(
    "/{group_id}/tomorrow",
    response=DaySchedule,
)
def get_tomorrow_schedule(
    request: HttpRequest,  # noqa: ARG001
    group_id: pydantic.UUID4,
    ignore_cache: bool = False,
) -> DaySchedule:
    date = timezone.now().date() + timedelta(days=1)
    day_schedule = get_day_schedule(
        group=read_group(group_id=group_id),
        for_day=date,
        ignore_cache=ignore_cache,
    )

    if day_schedule is None:
        raise HttpError(404, message=f"No schedule found for {date}")

    return day_schedule


@student_schedule_router.get(
    "/{group_id}/today",
    response=DaySchedule,
)
def get_today_schedule(
    request: HttpRequest,  # noqa: ARG001
    group_id: pydantic.UUID4,
    ignore_cache: bool = False,
) -> DaySchedule:
    date = timezone.now().date()
    day_schedule = get_day_schedule(
        group=read_group(group_id=group_id),
        for_day=date,
        ignore_cache=ignore_cache,
    )

    if day_schedule is None:
        raise HttpError(404, message=f"No schedule found for {date}")

    return day_schedule


@student_schedule_router.get(
    "/{group_id}/day/{for_day}",
    response=DaySchedule,
)
def get_specific_day_schedule(
    request: HttpRequest,  # noqa: ARG001
    group_id: pydantic.UUID4,
    for_day: datetime.date,
    ignore_cache: bool = False,
) -> DaySchedule:
    day_schedule = get_day_schedule(
        group=read_group(group_id=group_id),
        for_day=for_day,
        ignore_cache=ignore_cache,
    )

    if day_schedule is None:
        raise HttpError(404, message=f"No schedule found for {for_day}")

    return day_schedule


@teacher_schedule_router.get(
    "/{teacher_id}",
    response=WeekSchedule,
)
def get_teacher_schedule(
    request: HttpRequest,  # noqa: ARG001
    teacher_id: pydantic.UUID4,
    ignore_cache: bool = False,
) -> WeekSchedule:
    teacher = read_teacher(teacher_id=teacher_id)

    return get_week_schedule(
        teacher=teacher,
        ignore_cache=ignore_cache,
    )


@teacher_schedule_router.get(
    "/{teacher_id}/day/{for_day}",
    response=DaySchedule,
)
def get_teacher_day_schedule(
    request: HttpRequest,  # noqa: ARG001
    teacher_id: pydantic.UUID4,
    for_day: datetime.date,
    ignore_cache: bool = False,
) -> DaySchedule:
    teacher = read_teacher(teacher_id=teacher_id)

    day_schedule = get_day_schedule(
        teacher=teacher,
        for_day=for_day,
        ignore_cache=ignore_cache,
    )

    if day_schedule is None:
        raise HttpError(404, message=f"No schedule found for {for_day}")

    return day_schedule


schedule_router.add_router("/student", student_schedule_router)
schedule_router.add_router("/teacher", teacher_schedule_router)
public_router.add_router("/schedule", schedule_router)
