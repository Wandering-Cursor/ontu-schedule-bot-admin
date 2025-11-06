import datetime

import pydantic

from ontu_schedule_admin.api.schemas.base import APISchema


class Teacher(APISchema):
    short_name: str = pydantic.Field(examples=["Іванов І.І."])
    full_name: str = pydantic.Field(examples=["Іванов Іван Іванович"])


class Lesson(APISchema):
    short_name: str = pydantic.Field(examples=["ПНМ (Онлайн лек.)"])
    full_name: str = pydantic.Field(examples=["Професійно-наукова мова"])

    teacher: Teacher

    card: str | None = pydantic.Field(
        default=None,
        examples=[
            "Ідентифікатор конференції: XXX YYY ZZZ\r\nКод доступу: ABCDEFG",
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
    date: datetime.date

    pairs: list[Pair]


class WeekSchedule(APISchema):
    days: list[DaySchedule]
