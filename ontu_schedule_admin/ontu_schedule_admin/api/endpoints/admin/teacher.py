from django.http import HttpRequest  # noqa: TC002
from django.views.decorators.csrf import csrf_exempt
from main.operations.teacher import update_teachers_from_api

from ontu_schedule_admin.api.schemas.teacher import FetchTeacherRequest  # noqa: TC001
from ontu_schedule_admin.api.utils.log import make_log

from .router import admin_router


@admin_router.post(
    "/teacher/fetch",
)
@csrf_exempt
def fetch_teachers(
    request: HttpRequest,
    body: FetchTeacherRequest,
) -> bool:
    """
    Fetch all teachers.
    """
    make_log(
        {
            "msg": "Request to fetch teachers from Schedule API",
            "user": request.user,
        },
        level="WARNING",
    )

    update_teachers_from_api(department_ids=body.department_id)

    make_log(
        {
            "msg": "Fetched teachers from Schedule API",
        }
    )

    return True
