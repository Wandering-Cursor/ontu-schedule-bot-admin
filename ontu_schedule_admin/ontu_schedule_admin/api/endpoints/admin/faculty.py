from django.http import HttpRequest  # noqa: TC002
from django.views.decorators.csrf import csrf_exempt
from main.operations.faculty import update_faculties_from_api

from ontu_schedule_admin.api.utils.log import make_log

from .router import admin_router


@admin_router.post(
    "/faculty/fetch",
)
@csrf_exempt
def fetch_faculty(request: HttpRequest) -> bool:
    """
    Fetch all faculties.
    """
    make_log(
        {
            "msg": "Request to fetch faculties from Schedule API",
            "user": request.user,
        },
        level="WARNING",
    )

    update_faculties_from_api()

    make_log(
        {
            "msg": "Fetched departments from Schedule API",
        }
    )

    return True
