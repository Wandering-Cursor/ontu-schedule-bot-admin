import logging
from functools import wraps
from time import sleep
from typing import Any, Callable, TypeVar, cast, overload

F = TypeVar("F", bound=Callable[..., Any])


@overload
def do_until_success(__func: F) -> F: ...


@overload
def do_until_success(
    *,
    number_of_tries: int = 3,
) -> Callable[[F], F]: ...


def do_until_success(
    work_func: F | None = None,
    *,
    number_of_tries: int = 3,
) -> F | Callable[[F], F]:
    def decorator(work_func: F) -> F:
        @wraps(work_func)
        def wrapper(*args: tuple[Any], **kwargs: dict[str, Any]) -> Any:
            last_exception = None
            delay = 1
            tries = number_of_tries
            while tries:
                tries -= 1
                result = object
                try:
                    result = work_func(*args, **kwargs)
                except Exception as e:
                    from .operations import global_parser

                    last_exception = e
                    global_parser.sender.cookies._value = None

                    logging.warning(
                        f"During exectution of {work_func.__name__} raised exeption {e}"
                    )
                if result != object:
                    return result
                if tries:
                    sleep(delay)

            raise Exception(
                f"Tried to wait for the response from `{work_func.__name__}`, "
                f"but gived up after {number_of_tries} tries.",
                last_exception,
            )

        return cast(F, wrapper)

    if work_func is not None:
        return decorator(work_func)
    else:
        return decorator
