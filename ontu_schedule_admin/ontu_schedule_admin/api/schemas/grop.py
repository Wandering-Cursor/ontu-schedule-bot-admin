import pydantic

from ontu_schedule_admin.api.schemas.base import APISchema


class FetchGroupsRequest(APISchema):
    faculty_id: list[pydantic.UUID4] | None = pydantic.Field(
        default=None,
        description="List of faculty IDs to fetch groups for. If None, fetch for all faculties.",
    )
