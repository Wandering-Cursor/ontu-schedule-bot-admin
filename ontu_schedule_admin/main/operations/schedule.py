from __future__ import annotations

import json
from typing import TYPE_CHECKING, cast

from django.core.cache import cache
from django.utils import timezone
from main.enums import ScheduleEntityType
from main.models.subscription import Subscription
from main.operations.third_party.errors import ScheduleAPIError
from main.operations.third_party.schedule_api import (
    get_student_schedule_by_group as api_get_schedule_by_group,
)
from main.operations.third_party.schedule_api import get_teacher_schedule_by_teacher
from ontu_schedule_admin.api.schemas.schedule import (
    BulkScheduleItem,
    DaySchedule,
    Lesson,
    Pair,
    ScheduleEntity,
    WeekSchedule,
)
from ontu_schedule_admin.api.schemas.teacher import ScheduleTeacherInfo, TeacherInfo
from ontu_schedule_admin.api.utils.log import make_log

if TYPE_CHECKING:
    import datetime
    from collections.abc import AsyncGenerator, Awaitable, Callable

    from main.models.group import Group
    from main.models.teacher import Teacher
    from ontu_parser.dataclasses import StudentsPair, TeachersPair


def _process_student_pairs(pairs: list[StudentsPair]) -> list[Pair]:
    """Process pairs for student schedule."""
    return [
        Pair(
            number=pair.pair_no or 0,
            lessons=[
                Lesson(
                    short_name=lesson.lesson_name["short"],
                    full_name=lesson.lesson_name["full"],
                    teacher=ScheduleTeacherInfo(
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
    ]


def _process_teacher_pairs(
    pairs: list[TeachersPair],
    teacher: Teacher,
    teacher_department_ids: list,
) -> list[Pair]:
    """Process pairs for teacher schedule."""
    return [
        Pair(
            number=pair.pair_no,
            lessons=[
                Lesson(
                    short_name=pair.lesson.name,
                    full_name=pair.lesson.name,
                    teacher=TeacherInfo(
                        uuid=teacher.uuid,
                        short_name=teacher.short_name,
                        full_name=teacher.full_name,
                        departments=teacher_department_ids,
                    ),
                    card=pair.lesson.groups,
                )
            ]
            if pair.lesson
            else [],
        )
        for pair in pairs
    ]


async def _get_week_schedule(
    entity: Group | Teacher,
    entity_type: ScheduleEntityType,
    api_fetch_func: Callable[..., Awaitable[dict]],
    pairs_processor: Callable,
    ignore_cache: bool = False,
) -> WeekSchedule:
    """
    Universal method to fetch and cache weekly schedule.

    Args:
        entity: The group or teacher entity
        entity_type: ScheduleEntityType identifier for the entity type (e.g., 'group', 'teacher')
        api_fetch_func: Function to call the external API
        pairs_processor: Function to process pairs specific to entity type
        ignore_cache: Whether to bypass cache

    Returns:
        WeekSchedule object
    """
    cache_key = f"{entity.uuid}_{entity_type}_schedule"

    if not ignore_cache:
        cached_schedule = await cache.aget(cache_key)
        if cached_schedule is not None:
            make_log(
                {
                    "msg": f"Schedule for {entity_type} {entity.short_name} fetched from cache",
                },
                level="INFO",
            )
            return cached_schedule

    api_schedule = await api_fetch_func(entity)

    teacher_department_ids = []
    if entity_type == ScheduleEntityType.TEACHER:
        teacher_entity = cast("Teacher", entity)
        teacher_department_ids = [
            department_id
            async for department_id in teacher_entity.departments.values_list("uuid", flat=True)
        ]

    schedule_entity = ScheduleEntity(
        type=entity_type,
        uuid=entity.uuid,
        short_name=entity.short_name,
        full_name=getattr(entity, "full_name", None),
        external_id=getattr(entity, "external_id", None),
        short_id=await entity.get_short_id(),
    )

    schedule = WeekSchedule(
        for_entity=entity.short_name,
        entity=schedule_entity,
        days=[],
    )
    for date, pairs in api_schedule.items():
        kwargs = {}
        if entity_type == ScheduleEntityType.TEACHER:
            kwargs["teacher"] = entity
            kwargs["teacher_department_ids"] = teacher_department_ids

        schedule.days.append(
            DaySchedule(
                for_entity=entity.short_name,
                entity=schedule_entity,
                date=date,
                pairs=pairs_processor(pairs, **kwargs),
            )
        )

    await cache.aset(cache_key, schedule, timeout=60 * 15)

    make_log(
        {
            "msg": f"Schedule for {entity_type} {entity.short_name} cached",
        },
        level="WARNING",
    )

    return schedule


async def _get_day_schedule(  # noqa: PLR0913
    entity: Group | Teacher,
    entity_type: ScheduleEntityType,
    for_day: datetime.date,
    api_fetch_func: Callable[..., Awaitable[dict]],
    pairs_processor: Callable,
    ignore_cache: bool = False,
) -> DaySchedule | None:
    """
    Universal method to fetch a specific day's schedule.

    Args:
        entity: The group or teacher entity
        entity_type: ScheduleEntityType identifier for the entity type (e.g., 'group', 'teacher')
        for_day: The date to fetch schedule for
        api_fetch_func: Function to call the external API
        pairs_processor: Function to process pairs specific to entity type
        ignore_cache: Whether to bypass cache

    Returns:
        DaySchedule object or None if not found
    """
    cache_key = f"{entity.uuid}_{entity_type}_schedule_{for_day.isoformat()}"
    if not ignore_cache:
        cached_day_schedule = await cache.aget(cache_key)
        if cached_day_schedule is not None:
            make_log(
                {
                    "msg": (
                        f"Day schedule for {entity_type} {entity.short_name}"
                        f"on {for_day} fetched from cache"
                    ),
                },
                level="INFO",
            )
            return cached_day_schedule

    full_schedule = await _get_week_schedule(
        entity=entity,
        entity_type=entity_type,
        api_fetch_func=api_fetch_func,
        pairs_processor=pairs_processor,
        ignore_cache=ignore_cache,
    )

    for day in full_schedule.days:
        if day.date == for_day:
            await cache.aset(cache_key, day, timeout=60 * 5)
            return day

    return None


async def get_week_schedule(
    group: Group | None = None,
    teacher: Teacher | None = None,
    ignore_cache: bool = False,
) -> WeekSchedule:
    """Fetch weekly schedule for a group or teacher."""
    if group:
        return await _get_week_schedule(
            entity=group,
            entity_type=ScheduleEntityType.GROUP,
            api_fetch_func=lambda g: api_get_schedule_by_group(group=g),
            pairs_processor=_process_student_pairs,
            ignore_cache=ignore_cache,
        )
    if teacher:
        return await _get_week_schedule(
            entity=teacher,
            entity_type=ScheduleEntityType.TEACHER,
            api_fetch_func=lambda t: get_teacher_schedule_by_teacher(teacher=t),
            pairs_processor=_process_teacher_pairs,
            ignore_cache=ignore_cache,
        )

    raise ValueError("Either group or teacher must be provided.")


async def get_day_schedule(
    for_day: datetime.date,
    group: Group | None = None,
    teacher: Teacher | None = None,
    ignore_cache: bool = False,
) -> DaySchedule | None:
    """Fetch daily schedule for a group or teacher."""
    if group:
        return await _get_day_schedule(
            entity=group,
            entity_type=ScheduleEntityType.GROUP,
            for_day=for_day,
            api_fetch_func=lambda g: api_get_schedule_by_group(group=g),
            pairs_processor=_process_student_pairs,
            ignore_cache=ignore_cache,
        )
    if teacher:
        return await _get_day_schedule(
            entity=teacher,
            entity_type=ScheduleEntityType.TEACHER,
            for_day=for_day,
            api_fetch_func=lambda t: get_teacher_schedule_by_teacher(teacher=t),
            pairs_processor=_process_teacher_pairs,
            ignore_cache=ignore_cache,
        )

    raise ValueError("Either group or teacher must be provided.")


async def get_schedule_in_bulk() -> AsyncGenerator[str]:
    yield "[\n"

    is_first = True
    try:
        subscriptions = (
            Subscription.objects.filter(
                is_active=True,
                chat__isnull=False,
            )
            .select_related("chat")
            .prefetch_related("groups", "teachers")
        )

        async for subscription in subscriptions:
            if not is_first:
                yield ",\n"
            else:
                is_first = False

            chat = subscription.chat

            schedules: list[DaySchedule | None] = []
            async for group in subscription.groups.all():
                try:
                    schedule = await get_day_schedule(
                        for_day=timezone.now().date(),
                        group=group,
                    )
                except ScheduleAPIError:
                    continue
                schedules.append(schedule)

            async for teacher in subscription.teachers.all():
                try:
                    schedule = await get_day_schedule(
                        for_day=timezone.now().date(),
                        teacher=teacher,
                    )
                except ScheduleAPIError:
                    continue
                schedules.append(schedule)

            yield (
                json.dumps(
                    {
                        chat.platform_chat_id: [
                            s.model_dump(mode="json") if s else None for s in schedules
                        ]
                    }
                )
            )
    except Exception as e:  # noqa: BLE001
        make_log(
            {
                "msg": "Error during bulk schedule retrieval",
                "error": str(e),
            },
            level="ERROR",
        )
        return

    yield "\n]"


async def get_schedule_in_bulk_objects() -> AsyncGenerator[BulkScheduleItem]:
    """
    Similar to get_schedule_in_bulk but yields deserialized objects instead of JSON strings.

    Yields:
        Dictionary with platform_chat_id as key and list of DaySchedule or None as value.
    """
    try:
        subscriptions = (
            Subscription.objects.filter(
                is_active=True,
                chat__isnull=False,
            )
            .select_related("chat")
            .prefetch_related("groups", "teachers")
        )

        async for subscription in subscriptions:
            chat = subscription.chat

            schedules: list[DaySchedule | None] = []

            async for group in subscription.groups.all():
                try:
                    schedule = await get_day_schedule(
                        for_day=timezone.now().date(),
                        group=group,
                    )
                except ScheduleAPIError:
                    continue
                schedules.append(schedule)

            async for teacher in subscription.teachers.all():
                try:
                    schedule = await get_day_schedule(
                        for_day=timezone.now().date(),
                        teacher=teacher,
                    )
                except ScheduleAPIError:
                    continue
                schedules.append(schedule)

            yield BulkScheduleItem(
                platform_chat_id=chat.platform_chat_id,
                schedules=schedules,
            )
    except Exception as e:  # noqa: BLE001
        make_log(
            {
                "msg": "Error during bulk schedule retrieval",
                "error": str(e),
            },
            level="ERROR",
        )
        return
