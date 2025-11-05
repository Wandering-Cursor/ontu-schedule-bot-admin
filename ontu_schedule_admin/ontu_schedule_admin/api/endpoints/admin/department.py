from django.http import HttpRequest  # noqa: TC002
from django.views.decorators.csrf import csrf_exempt
from main.operations.department import update_departments_from_api

from ontu_schedule_admin.api.utils.log import make_log

from .router import admin_router


@admin_router.post(
    "/department/fetch",
)
@csrf_exempt
def fetch_departments(request: HttpRequest) -> bool:
    """
    Fetch all departments.
    """
    make_log(
        {
            "msg": "Request to fetch departments from Schedule API",
            "user": request.user,
        },
        level="WARNING",
    )

    update_departments_from_api()

    make_log(
        {
            "msg": "Fetched departments from Schedule API",
        }
    )

    return True
