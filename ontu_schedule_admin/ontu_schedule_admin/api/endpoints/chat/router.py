from ninja import Router

from ontu_schedule_admin.api.auth import AppAuthentication

chat_router = Router(
    tags=[
        "Chat",
    ],
    auth=AppAuthentication(),
)
