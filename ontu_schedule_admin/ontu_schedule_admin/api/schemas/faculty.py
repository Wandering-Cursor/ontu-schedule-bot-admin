from pydantic import UUID4  # noqa: TC002

from ontu_schedule_admin.api.schemas.base import Schema


class Faculty(Schema):
    uuid: UUID4

    short_name: str
