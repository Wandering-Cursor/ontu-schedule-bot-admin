import functools
from typing import TYPE_CHECKING, ParamSpec, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

P = ParamSpec("P")
T = TypeVar("T")


def catch_api_exception[**P, T](func: Callable[P, T]) -> Callable[P, T]:
    """Decorator to catch API exceptions and log them."""

    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if len(e.args) >= 2 and e.args[1] == 503:  # noqa: PLR2004
                from main.operations.third_party.schedule_api import (  # noqa: PLC0415
                    global_parser,
                    global_teacher_parser,
                )

                global_parser.sender.cookies._value = None  # noqa: SLF001
                global_teacher_parser.sender.cookies._value = None  # noqa: SLF001

                return func(*args, **kwargs)
            raise e

    return wrapper
