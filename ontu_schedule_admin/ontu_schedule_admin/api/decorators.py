import asyncio
from functools import wraps
from inspect import isawaitable
from typing import TYPE_CHECKING
from uuid import uuid4

from asgiref.sync import sync_to_async
from django.db import connections, reset_queries

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


def close_old_connections_custom() -> None:
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


def close_old_connections_decorator(func) -> object:  # noqa: ANN001
    """Must be used in `view` mode to work."""
    if asyncio.iscoroutinefunction(func):

        @wraps(func)
        async def wrapper(request: HttpRequest, *args: object, **kwargs: object) -> object:  # type: ignore
            reset_queries()
            close_old_connections_custom()
            await sync_to_async(reset_queries)()
            await sync_to_async(close_old_connections_custom)()

            result = func(request, *args, **kwargs)

            if isawaitable(result):
                result = await result

            return result

        return wrapper

    @wraps(func)
    def wrapper(request: HttpRequest, *args: object, **kwargs: object) -> object:
        reset_queries()
        close_old_connections_custom()

        return func(request, *args, **kwargs)

    return wrapper
