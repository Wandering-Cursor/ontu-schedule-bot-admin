from django.http import HttpRequest  # noqa: TC002
from django.views.decorators.csrf import csrf_exempt
from main.operations.group import update_groups_from_api

from ontu_schedule_admin.api.schemas.grop import FetchGroupsRequest  # noqa: TC001
from ontu_schedule_admin.api.utils.log import make_log

from .router import admin_router


@admin_router.post(
    "/group/fetch",
)
@csrf_exempt
def fetch_groups(
    request: HttpRequest,
    body: FetchGroupsRequest,
) -> bool:
    """
    Fetch all groups.
    """
    make_log(
        {
            "msg": "Request to fetch groups from Schedule API",
            "user": request.user,
        },
        level="WARNING",
    )

    update_groups_from_api(faculty_ids=body.faculty_id)

    make_log(
        {
            "msg": "Fetched groups from Schedule API",
        }
    )

    return True
