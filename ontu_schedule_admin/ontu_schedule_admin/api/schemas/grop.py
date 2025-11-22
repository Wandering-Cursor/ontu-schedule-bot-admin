import pydantic

from ontu_schedule_admin.api.schemas.base import (
    APISchema,
    PaginatedRequest,
    PaginatedResponse,
    Schema,
)
from ontu_schedule_admin.api.schemas.faculty import Faculty  # noqa: TC001


class FetchGroupsRequest(APISchema):
    faculty_id: list[pydantic.UUID4] | None = pydantic.Field(
        default=None,
        description="List of faculty IDs to fetch groups for. If None, fetch for all faculties.",
    )


class Group(Schema):
    uuid: pydantic.UUID4

    short_name: str
    faculty: Faculty


class GroupInfo(Schema):
    uuid: pydantic.UUID4

    short_name: str
    faculty_id: pydantic.UUID4


class GroupPaginatedRequest(PaginatedRequest):
    faculty_id: pydantic.UUID4 | None = pydantic.Field(
        default=None,
        description="Filter groups by faculty ID.",
    )
    name: str | None = pydantic.Field(
        default=None,
        description="Filter groups by name (partial match).",
    )


class GroupPaginatedResponse(PaginatedResponse[Group]):
    pass
