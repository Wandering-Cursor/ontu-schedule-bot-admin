import pydantic  # noqa: TC002

from ontu_schedule_admin.api.schemas.base import Schema


class Department(Schema):
    uuid: pydantic.UUID4

    short_name: str
    full_name: str
