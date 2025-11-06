import pydantic  # noqa: TC002
from django.http import HttpRequest  # noqa: TC002
from main.operations.group import read_group
from main.operations.schedule import get_schedule_by_group
from ninja import Router

from .router import public_router

schedule_router = Router(
    tags=[
        "Schedule",
    ],
)


@schedule_router.get(
    "/{group_id}",
)
def get_schedule(
    request: HttpRequest,
    group_id: pydantic.UUID4,
) -> dict:
    group = read_group(group_id=group_id)

    return get_schedule_by_group(
        group=group,
    )


public_router.add_router("/schedule", schedule_router)
