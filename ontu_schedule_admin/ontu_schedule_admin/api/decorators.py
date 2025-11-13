from functools import wraps
from typing import TYPE_CHECKING
from uuid import uuid4

from ontu_schedule_admin.api.utils.log import RequestContextVar

if TYPE_CHECKING:
    from django.http import HttpRequest


def request_id_decorator(func) -> object:  # noqa: ANN001
    """Must be used in `view` mode to work."""

    @wraps(func)
    def wrapper(request: HttpRequest, *args: object, **kwargs: object) -> object:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        response_id = str(uuid4())

        request.request_id = request_id  # type: ignore
        request.response_id = response_id  # type: ignore

        RequestContextVar.set(request)

        response = func(request, *args, **kwargs)

        response["X-Request-ID"] = request_id
        response["X-Response-ID"] = response_id

        return response

    return wrapper
