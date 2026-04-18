import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponsePermanentRedirect  # noqa: TC002
from django.shortcuts import redirect
from main.operations.third_party.errors import CookiesExpiredError, IsOnBreakError, ScheduleAPIError
from ninja import NinjaAPI
from ontu_schedule_admin.api.decorators import close_old_connections_decorator, request_id_decorator
from ontu_schedule_admin.api.endpoints.admin.router import admin_router
from ontu_schedule_admin.api.endpoints.chat.router import chat_router
from ontu_schedule_admin.api.endpoints.public.router import public_router
from ontu_schedule_admin.api.utils.log import make_log

app = NinjaAPI()

app.add_decorator(
    request_id_decorator,
    mode="view",
)
app.add_decorator(
    close_old_connections_decorator,
    mode="view",
)


@app.exception_handler(ObjectDoesNotExist)
def handle_does_not_exist(
    request,  # noqa: ANN001
    exc: ObjectDoesNotExist,
) -> HttpResponse:
    make_log(
        message={
            "msg": "Requested object does not exist.",
            "exception": {
                "str": str(exc),
                "traceback": traceback.format_exc(),
            },
        },
        level="ERROR",
    )

    return app.create_response(
        request,
        data={
            "msg": "Requested object does not exist.",
        },
        status=404,
    )


@app.exception_handler(IsOnBreakError)
def handle_is_on_break_error(
    request,  # noqa: ANN001
    exc: IsOnBreakError,
) -> HttpResponse:
    make_log(
        message={
            "msg": "Schedule API is currently on break.",
            "exception": {
                "str": str(exc),
                "traceback": traceback.format_exc(),
            },
        },
        level="ERROR",
    )

    return app.create_response(
        request,
        data={
            "msg": "Schedule API is currently on break.",
        },
        status=503,
    )


@app.exception_handler(CookiesExpiredError)
def handle_cookies_expired_error(
    request,  # noqa: ANN001
    exc: CookiesExpiredError,
) -> HttpResponse:
    make_log(
        message={
            "msg": "Schedule API cookies are expired.",
            "exception": {
                "str": str(exc),
                "traceback": traceback.format_exc(),
            },
        },
        level="ERROR",
    )

    return app.create_response(
        request,
        data={
            "msg": "Schedule API cookies are expired.\nPlease, try again.",
        },
        status=400,
    )


@app.exception_handler(ScheduleAPIError)
def handle_schedule_api_error(
    request,  # noqa: ANN001
    exc: ScheduleAPIError,
) -> HttpResponse:
    make_log(
        message={
            "msg": "An unknown error occurred while processing the schedule API response.",
            "exception": {
                "str": str(exc),
                "traceback": traceback.format_exc(),
            },
        },
        level="ERROR",
    )

    return app.create_response(
        request,
        data={
            "msg": "An unknown error occurred while processing the schedule API response.\nPlease, try again later.",
        },
        status=500,
    )


@app.get(
    "/",
    include_in_schema=False,
)
def root(request: object) -> HttpResponsePermanentRedirect:  # noqa: ARG001
    return redirect(
        "/api/docs",
        permanent=True,
    )


app.add_router("/admin/", admin_router)
app.add_router("/public/", public_router)
app.add_router("/chat/", chat_router)
