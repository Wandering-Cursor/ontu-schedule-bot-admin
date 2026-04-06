"""
Bulk operations are used by Telegram Bot co-developed for this API.

They are using authenticated requests to prevent abuse.
"""

from django.db import transaction
from django.http import HttpRequest, StreamingHttpResponse
from main.operations.schedule import get_schedule_in_bulk, get_schedule_in_bulk_objects
from ninja import Router
from ninja.streaming import SSE
from ontu_schedule_admin.api.schemas.schedule import BulkScheduleItem, DaySchedule

from .router import chat_router

bulk_router = Router(
    tags=(chat_router.tags or [])
    + [
        "Bulk",
    ],
)


@bulk_router.get(
    "/schedule",
    tags=(chat_router.tags or []) + ["Bulk"],
    response={200: dict[str, list[DaySchedule | None]]},
)
@transaction.atomic()
def get_data(request: HttpRequest) -> StreamingHttpResponse:  # noqa: ARG001
    """
    Return a streaming response of schedule data for sending in bulk to chat users.
    Keys are chat ids and values are lists of DaySchedule or None.
    """
    return StreamingHttpResponse(get_schedule_in_bulk(), content_type="application/json")  # pyright: ignore[reportArgumentType]


@bulk_router.get(
    "/schedule-sse",
    tags=(chat_router.tags or []) + ["Bulk"],
    response=SSE[BulkScheduleItem],
)
@transaction.atomic()
def get_data_sse(request: HttpRequest):  # noqa: ANN201, ARG001
    """
    Get a streaming response (SSE format) of schedule data for sending in bulk to chat users.
    Each item is a BulkScheduleItem containing a platform_chat_id and a list of DaySchedule or None.
    """
    yield from get_schedule_in_bulk_objects()


chat_router.add_router("/bulk", bulk_router)
