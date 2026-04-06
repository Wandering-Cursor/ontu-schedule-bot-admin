import datetime  # noqa: TC003

import pydantic
from main.enums import ScheduleEntityType  # noqa: TC002
from ontu_schedule_admin.api.schemas.base import APISchema
from ontu_schedule_admin.api.schemas.teacher import ScheduleTeacherInfo, TeacherInfo  # noqa: TC002


class ScheduleEntity(APISchema):
    type: ScheduleEntityType

    uuid: pydantic.UUID4

    short_name: str
    full_name: str | None
    external_id: str | None = pydantic.Field(description="As seen in the ONTU Rozklad system.")

    short_id: str = pydantic.Field(
        description="Might be useful for quick checks. Note that uniqueness is not guaranteed.",
    )


class Lesson(APISchema):
    short_name: str = pydantic.Field(examples=["ПНМ (Онлайн лек.)"])
    full_name: str = pydantic.Field(examples=["Професійно-наукова мова"])

    teacher: TeacherInfo | ScheduleTeacherInfo

    card: str | None = pydantic.Field(
        default=None,
        examples=[
            "Ідентифікатор конференції: XXX YYY ZZZ\r\nКод доступу: ABCDEFG",  # noqa: RUF001
        ],
    )
    auditorium: str | None = pydantic.Field(
        default=None,
        examples=["B-123", "Онлайн"],
    )


class Pair(APISchema):
    number: int = pydantic.Field(
        ge=1,
    )

    lessons: list[Lesson]


class DaySchedule(APISchema):
    for_entity: str = pydantic.Field(
        deprecated=True,
        description="Will be replaced by `entity` field in the future.",
    )
    entity: ScheduleEntity

    date: datetime.date

    pairs: list[Pair]


class WeekSchedule(APISchema):
    for_entity: str = pydantic.Field(
        deprecated=True,
        description="Will be replaced by `entity` field in the future.",
    )
    entity: ScheduleEntity

    days: list[DaySchedule]


class BulkScheduleItem(APISchema):
    platform_chat_id: str
    schedules: list[DaySchedule | None]
