import functools
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from httpx import HTTPStatusError
from main.operations.third_party.errors import (
    CookiesExpiredError,
    FacultyNotFoundError,
    IsOnBreakError,
    ScheduleAPIError,
)
from ontu_parser.errors import ParsingError
from ontu_schedule_admin.api.utils.log import make_log

if TYPE_CHECKING:
    from collections.abc import Callable

P = ParamSpec("P")
T = TypeVar("T")


def catch_api_exception[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to catch API exceptions and log them."""

    if iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return await func(*args, **kwargs)
            except FacultyNotFoundError as e:
                from main.operations.third_party.schedule_api import (  # noqa: PLC0415
                    is_schedule_api_on_break,
                )

                if await is_schedule_api_on_break():
                    raise IsOnBreakError("Schedule API is currently on break.") from e

                raise e
            except ParsingError as e:
                from main.operations.third_party.schedule_api import (  # noqa: PLC0415
                    reset_parser_cache,
                )

                make_log(
                    {
                        "msg": "Parsing error in schedule API response.",
                        "content": e.content,
                    },
                    level="ERROR",
                )

                if (
                    isinstance(e.underlying_error, HTTPStatusError)
                    and e.underlying_error.response.status_code == 503  # noqa: PLR2004
                ):
                    make_log(
                        {
                            "msg": (
                                "Schedule API returned 503 Service Unavailable. "
                                "Clearing parser cache."
                            ),
                            "error": e,
                        },
                        level="WARNING",
                    )
                    await reset_parser_cache()

                    raise CookiesExpiredError(
                        "Schedule API cookies are expired. Parser cache has been cleared."
                    ) from e

                raise ScheduleAPIError(
                    "An error occurred while parsing the schedule API response.",
                    e.content,
                    e,
                ) from e

        return async_wrapper  # pyright: ignore[reportReturnType]

    raise NotImplementedError("Only async functions are supported by this decorator.")
