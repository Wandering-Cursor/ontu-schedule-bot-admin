import json
import logging
from contextvars import ContextVar
from typing import TYPE_CHECKING, Literal

from django.utils import timezone

if TYPE_CHECKING:
    from django.http import HttpRequest

main_logger = logging.getLogger("ontu_schedule_admin")
main_logger.setLevel(logging.INFO)

RequestContextVar = ContextVar("current_request")


def make_log(
    message: dict,
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO",
) -> None:
    request: HttpRequest = RequestContextVar.get(None)

    level_value = getattr(logging, level.upper(), logging.INFO)

    context = {}

    if request is not None:
        context = {
            "request": {
                "method": request.method,
                "path": request.path,
                "request_id": getattr(request, "request_id", None),
                "response_id": getattr(request, "response_id", None),
            },
            "time": timezone.now().isoformat(),
        }

    main_logger.log(
        level_value,
        json.dumps(
            {
                "message": message,
                "context": context,
            },
            default=repr,
        ),
    )
