import functools
from inspect import iscoroutinefunction
from typing import TYPE_CHECKING, ParamSpec, TypeVar

from main.operations.third_party.errors import FacultyNotFoundError, IsOnBreakError

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
                    async_global_parser,
                )

                if await async_global_parser.is_on_break():
                    raise IsOnBreakError("Schedule API is currently on break.") from e

                raise e

        return async_wrapper

    raise NotImplementedError("Only async functions are supported by this decorator.")
