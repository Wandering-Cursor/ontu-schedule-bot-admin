import pydantic

from ontu_schedule_admin.api.schemas.base import PaginatedRequest, PaginatedResponse, Schema


class Department(Schema):
    uuid: pydantic.UUID4

    short_name: str
    full_name: str


class DepartmentPaginatedRequest(PaginatedRequest):
    name: str | None = pydantic.Field(
        default=None,
        description="Filter departments by name (partial match).",
    )


class DepartmentPaginatedResponse(PaginatedResponse[Department]):
    pass
