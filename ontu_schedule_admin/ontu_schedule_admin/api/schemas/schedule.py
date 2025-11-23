import datetime  # noqa: TC003

import pydantic

from ontu_schedule_admin.api.schemas.base import APISchema
from ontu_schedule_admin.api.schemas.teacher import ScheduleTeacherInfo, TeacherInfo  # noqa: TC001


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
    for_entity: str

    date: datetime.date

    pairs: list[Pair]


class WeekSchedule(APISchema):
    for_entity: str

    days: list[DaySchedule]
