import pydantic  # noqa: TC002
from django.http import HttpRequest  # noqa: TC002

from .router import public_router


@public_router.get("/schedule")
def get_schedule(request: HttpRequest, group_id: pydantic.UUID4) -> dict:
    return {
        "msg": "TMP",
    }
