from django.http import HttpResponsePermanentRedirect  # noqa: TC002
from django.shortcuts import redirect
from ninja import NinjaAPI

from ontu_schedule_admin.api.decorators import request_id_decorator
from ontu_schedule_admin.api.endpoints.admin.router import admin_router
from ontu_schedule_admin.api.endpoints.public.router import public_router

app = NinjaAPI()

app.add_decorator(
    request_id_decorator,
    mode="view",
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
