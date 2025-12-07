import traceback

from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, HttpResponsePermanentRedirect  # noqa: TC002
from django.shortcuts import redirect
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
