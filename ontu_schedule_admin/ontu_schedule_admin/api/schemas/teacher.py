import pydantic

from ontu_schedule_admin.api.schemas.base import (
    APISchema,
    PaginatedRequest,
    PaginatedResponse,
    Schema,
)
from ontu_schedule_admin.api.schemas.department import Department  # noqa: TC001


class FetchTeacherRequest(APISchema):
    department_id: list[pydantic.UUID4] | None = pydantic.Field(
        default=None,
        description=(
            "List of department IDs to fetch teachers for. If None, fetch for all departments."
        ),
    )


class Teacher(Schema):
    uuid: pydantic.UUID4

    short_name: str
    full_name: str

    departments: list[Department]


class TeacherInfo(Schema):
    uuid: pydantic.UUID4

    short_name: str
    full_name: str

    departments: list[pydantic.UUID4]


class ScheduleTeacherInfo(Schema):
    """
    This class is used in palces that can only get
    teacher information from Schedule API.

    They don't have ID/Department information =>
    it's impossible to accurately link them to Teacher model.
    """

    short_name: str
    full_name: str


class TeacherPaginatedRequest(PaginatedRequest):
    department_id: pydantic.UUID4 | None = pydantic.Field(
        default=None,
        description="Filter teachers by department ID.",
    )

    name: str | None = pydantic.Field(
        default=None,
        description="Filter teachers by name (partial match).",
    )


class TeacherPaginatedResponse(PaginatedResponse[Teacher]):
    pass
