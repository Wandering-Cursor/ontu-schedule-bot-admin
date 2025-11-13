from ontu_schedule_admin.api.schemas.base import Schema
from ontu_schedule_admin.api.schemas.grop import Group  # noqa: TC001
from ontu_schedule_admin.api.schemas.teacher import Teacher  # noqa: TC001


class Subscription(Schema):
    is_active: bool

    groups: list[Group]
    teachers: list[Teacher]
