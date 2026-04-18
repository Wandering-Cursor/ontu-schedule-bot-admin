"""
Allows to get schedule for authenticated (via chat) users.
"""

import datetime
from typing import TYPE_CHECKING

from django.http import HttpRequest  # noqa: TC002
from django.utils import timezone
from main.operations import schedule as schedule_ops
from ninja import Router
from ninja.params.functions import Header as HeaderF
from ontu_schedule_admin.api.auth import ChatAuthentication
from ontu_schedule_admin.api.schemas.schedule import DaySchedule, WeekSchedule

from .router import chat_router

if TYPE_CHECKING:
    from ontu_schedule_admin.api.schemas.auth import ChatAuthenticationSchema

schedule_router = Router(
    tags=(chat_router.tags or [])
    + [
        "Schedule",
    ],
    auth=ChatAuthentication(),
)


@schedule_router.get(
    "/tomorrow",
    response=list[DaySchedule | None],
)
async def get_tomorrow_schedule(
    request: HttpRequest,
    chat_id: str = HeaderF(alias="X-Chat-ID"),  # noqa: ARG001
) -> list[DaySchedule | None]:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    for_day = timezone.now().date() + datetime.timedelta(days=1)

    subscription = auth.chat.subscription

    if not subscription:
        return []

    schedules: list[DaySchedule | None] = []
    async for group in subscription.groups.all():
        schedules.append(await schedule_ops.get_day_schedule(for_day=for_day, group=group))
    async for teacher in subscription.teachers.all():
        schedules.append(await schedule_ops.get_day_schedule(for_day=for_day, teacher=teacher))
    return schedules


@schedule_router.get(
    "/today",
    response=list[DaySchedule | None],
)
async def get_today_schedule(
    request: HttpRequest,
    chat_id: str = HeaderF(alias="X-Chat-ID"),  # noqa: ARG001
) -> list[DaySchedule | None]:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    for_day = timezone.now().date()

    subscription = auth.chat.subscription

    if not subscription:
        return []

    schedules: list[DaySchedule | None] = []
    async for group in subscription.groups.all():
        schedules.append(await schedule_ops.get_day_schedule(for_day=for_day, group=group))
    async for teacher in subscription.teachers.all():
        schedules.append(await schedule_ops.get_day_schedule(for_day=for_day, teacher=teacher))
    return schedules


@schedule_router.get(
    "/week",
    response=list[WeekSchedule],
)
async def get_week_schedule(
    request: HttpRequest,
    chat_id: str = HeaderF(alias="X-Chat-ID"),  # noqa: ARG001
) -> list[WeekSchedule]:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    subscription = auth.chat.subscription

    if not subscription:
        return []

    schedules: list[WeekSchedule] = []
    async for group in subscription.groups.all():
        schedules.append(
            await schedule_ops.get_week_schedule(
                group=group,
            )
        )
    async for teacher in subscription.teachers.all():
        schedules.append(
            await schedule_ops.get_week_schedule(
                teacher=teacher,
            )
        )
    return schedules


@schedule_router.get(
    "/day/{for_date}",
    response=list[DaySchedule | None],
)
async def get_day_schedule(
    request: HttpRequest,
    for_date: datetime.date,
    chat_id: str = HeaderF(alias="X-Chat-ID"),  # noqa: ARG001
) -> list[DaySchedule | None]:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    subscription = auth.chat.subscription

    if not subscription:
        return []

    schedules: list[DaySchedule | None] = []
    async for group in subscription.groups.all():
        schedules.append(await schedule_ops.get_day_schedule(for_day=for_date, group=group))
    async for teacher in subscription.teachers.all():
        schedules.append(await schedule_ops.get_day_schedule(for_day=for_date, teacher=teacher))
    return schedules


chat_router.add_router("/schedule", schedule_router)
