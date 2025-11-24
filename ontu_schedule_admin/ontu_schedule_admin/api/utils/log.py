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


SENSITIVE_KEYS = {"password"}


def redact_sensitive_info(obj: object) -> object:
    if isinstance(obj, dict):
        return {
            k: "[REDACTED]" if k.lower() in SENSITIVE_KEYS else redact_sensitive_info(v)
            for k, v in obj.items()
        }

    if isinstance(obj, list):
        return [redact_sensitive_info(item) for item in obj]

    return obj


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

    redacted_message = redact_sensitive_info(message)
    main_logger.log(
        level_value,
        json.dumps(
            {
                "message": redacted_message,
                "context": context,
            },
            default=repr,
        ),
    )


def message_to_json(message: object) -> str:
    """
    Converts virtually any object to a JSON string
    uses json.dumps and default to `repr()`
    """
    try:
        return json.dumps(message, default=repr)
    except (TypeError, ValueError):
        return json.dumps(str(message))
