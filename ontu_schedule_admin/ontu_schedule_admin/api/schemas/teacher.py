import pydantic

from ontu_schedule_admin.api.schemas.base import APISchema


class FetchTeacherRequest(APISchema):
    department_id: list[pydantic.UUID4] | None = pydantic.Field(
        default=None,
        description=(
            "List of department IDs to fetch teachers for. If None, fetch for all departments."
        ),
    )
