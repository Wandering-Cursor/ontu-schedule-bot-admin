import pydantic
from ontu_schedule_admin.api.schemas.base import PaginatedRequest, PaginatedResponse, Schema
from pydantic import UUID4


class Faculty(Schema):
    uuid: UUID4

    short_name: str


class FacultyPaginatedRequest(PaginatedRequest):
    name: str | None = pydantic.Field(
        default=None,
        description="Filter faculties by name (partial match).",
    )


class FacultyPaginatedResponse(PaginatedResponse[Faculty]):
    pass
