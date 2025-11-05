from ninja import NinjaAPI

from ontu_schedule_admin.api.decorators import request_id_decorator

from .admin.router import admin_router

app = NinjaAPI()

app.add_decorator(
    request_id_decorator,
    mode="view",
)


app.add_router("/admin/", admin_router)
