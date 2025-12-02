import json
from typing import TYPE_CHECKING

from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from ontu_schedule_admin.api.schemas.schedule import (
    DaySchedule,
    Lesson,
    Pair,
    WeekSchedule,
)
from ontu_schedule_admin.api.schemas.teacher import ScheduleTeacherInfo, TeacherInfo
from ontu_schedule_admin.api.utils.log import make_log

from main.models.subscription import Subscription
from main.operations.third_party.schedule_api import (
    get_student_schedule_by_group as api_get_schedule_by_group,
)
from main.operations.third_party.schedule_api import get_teacher_schedule_by_teacher

if TYPE_CHECKING:
    import datetime
    from collections.abc import Callable, Generator

    from ontu_parser.classes.dataclasses import StudentsPair, TeachersPair

    from main.models.group import Group
    from main.models.teacher import Teacher


def _process_student_pairs(pairs: list[StudentsPair]) -> list[Pair]:
    """Process pairs for student schedule."""
    return [
        Pair(
            number=pair.pair_no,
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
                        departments=[dept.uuid for dept in teacher.departments.all()],
                    ),
                    card=pair.lesson.groups,
                )
            ]
            if pair.lesson
            else [],
        )
        for pair in pairs
    ]


def _get_week_schedule(
    entity: Group | Teacher,
    entity_type: str,
    api_fetch_func: Callable,
    pairs_processor: Callable,
    ignore_cache: bool = False,
) -> WeekSchedule:
    """
    Universal method to fetch and cache weekly schedule.

    Args:
        entity: The group or teacher entity
        entity_type: String identifier for the entity type (e.g., 'group', 'teacher')
        api_fetch_func: Function to call the external API
        pairs_processor: Function to process pairs specific to entity type
        ignore_cache: Whether to bypass cache

    Returns:
        WeekSchedule object
    """
    cache_key = f"{entity.uuid}_{entity_type}_schedule"

    if not ignore_cache:
        cached_schedule = cache.get(cache_key)
        if cached_schedule is not None:
            make_log(
                {
                    "msg": f"Schedule for {entity_type} {entity.short_name} fetched from cache",
                },
                level="INFO",
            )
            return cached_schedule

    api_schedule = api_fetch_func(entity)

    schedule = WeekSchedule(days=[], for_entity=entity.short_name)
    for date, pairs in api_schedule.items():
        kwargs = {}
        if entity_type == "teacher":
            kwargs["teacher"] = entity

        schedule.days.append(
            DaySchedule(
                for_entity=entity.short_name,
                date=date,
                pairs=pairs_processor(pairs, **kwargs),
            )
        )

    # Cache the result
    cache.set(cache_key, schedule, timeout=60 * 15)

    make_log(
        {
            "msg": f"Schedule for {entity_type} {entity.short_name} cached",
        },
        level="WARNING",
    )

    return schedule


def _get_day_schedule(  # noqa: PLR0913
    entity: Group | Teacher,
    entity_type: str,
    for_day: datetime.date,
    api_fetch_func: Callable,
    pairs_processor: Callable,
    ignore_cache: bool = False,
) -> DaySchedule | None:
    """
    Universal method to fetch a specific day's schedule.

    Args:
        entity: The group or teacher entity
        entity_type: String identifier for the entity type
        for_day: The date to fetch schedule for
        api_fetch_func: Function to call the external API
        pairs_processor: Function to process pairs specific to entity type
        ignore_cache: Whether to bypass cache

    Returns:
        DaySchedule object or None if not found
    """
    cache_key = f"{entity.uuid}_{entity_type}_schedule_{for_day.isoformat()}"
    if not ignore_cache:
        cached_day_schedule = cache.get(cache_key)
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

    full_schedule = _get_week_schedule(
        entity=entity,
        entity_type=entity_type,
        api_fetch_func=api_fetch_func,
        pairs_processor=pairs_processor,
        ignore_cache=ignore_cache,
    )

    for day in full_schedule.days:
        if day.date == for_day:
            cache.set(cache_key, day, timeout=60 * 5)
            return day

    return None


def get_week_schedule(
    group: Group | None = None,
    teacher: Teacher | None = None,
    ignore_cache: bool = False,
) -> WeekSchedule:
    """Fetch weekly schedule for a group or teacher."""
    if group:
        return _get_week_schedule(
            entity=group,
            entity_type="group",
            api_fetch_func=lambda g: api_get_schedule_by_group(group=g),
            pairs_processor=_process_student_pairs,
            ignore_cache=ignore_cache,
        )
    if teacher:
        return _get_week_schedule(
            entity=teacher,
            entity_type="teacher",
            api_fetch_func=lambda t: get_teacher_schedule_by_teacher(teacher=t),
            pairs_processor=_process_teacher_pairs,
            ignore_cache=ignore_cache,
        )

    raise ValueError("Either group or teacher must be provided.")


def get_day_schedule(
    for_day: datetime.date,
    group: Group | None = None,
    teacher: Teacher | None = None,
    ignore_cache: bool = False,
) -> DaySchedule | None:
    """Fetch daily schedule for a group or teacher."""
    if group:
        return _get_day_schedule(
            entity=group,
            entity_type="group",
            for_day=for_day,
            api_fetch_func=lambda g: api_get_schedule_by_group(group=g),
            pairs_processor=_process_student_pairs,
            ignore_cache=ignore_cache,
        )
    if teacher:
        return _get_day_schedule(
            entity=teacher,
            entity_type="teacher",
            for_day=for_day,
            api_fetch_func=lambda t: get_teacher_schedule_by_teacher(teacher=t),
            pairs_processor=_process_teacher_pairs,
            ignore_cache=ignore_cache,
        )

    raise ValueError("Either group or teacher must be provided.")


def get_schedule_in_bulk() -> Generator[str]:
    yield "[\n"

    is_first = True
    for subscription in Subscription.objects.filter(
        is_active=True,
        chat__isnull=False,
    ):
        if not is_first:
            yield ",\n"
        else:
            is_first = False

        try:
            chat = subscription.chat
        except ObjectDoesNotExist:
            continue

        schedules: list[DaySchedule | None] = []
        for group in subscription.groups.all():
            schedule = get_day_schedule(
                for_day=timezone.now().date(),
                group=group,
            )
            schedules.append(schedule)
        for teacher in subscription.teachers.all():
            schedule = get_day_schedule(
                for_day=timezone.now().date(),
                teacher=teacher,
            )
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

    yield "\n]"
