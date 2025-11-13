from typing import TYPE_CHECKING

from django.http import HttpRequest
from django.utils import timezone
from main.models.api_user import APIUser
from main.models.chat import Chat
from ninja.security import HttpBasicAuth

from ontu_schedule_admin.api.schemas.auth import ChatAuthenticationSchema
from ontu_schedule_admin.api.utils.log import make_log

if TYPE_CHECKING:
    from django.http import HttpRequest


class AppAuthentication(HttpBasicAuth):
    def authenticate(
        self,
        request: HttpRequest,
        username: str,
        password: str,
    ) -> APIUser | None:
        try:
            user = APIUser.objects.get(username=username)
        except APIUser.DoesNotExist:
            make_log(
                {
                    "msg": "ChatAuthentication: User does not exist",
                    "username": username,
                    "request": {
                        "path": request.path,
                        "method": request.method,
                        "headers": dict(request.headers),
                        "ip": {
                            "REMOTE_ADDR": request.META.get("REMOTE_ADDR"),
                            "HTTP_X_FORWARDED_FOR": request.META.get("HTTP_X_FORWARDED_FOR"),
                        },
                    },
                },
                level="WARNING",
            )
            return None

        if not user.check_password(password):
            make_log(
                {
                    "msg": "ChatAuthentication: Invalid password",
                    "username": username,
                    "request": {
                        "path": request.path,
                        "method": request.method,
                        "headers": dict(request.headers),
                        "ip": {
                            "REMOTE_ADDR": request.META.get("REMOTE_ADDR"),
                            "HTTP_X_FORWARDED_FOR": request.META.get("HTTP_X_FORWARDED_FOR"),
                        },
                    },
                },
                level="WARNING",
            )
            return None

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        return user


class ChatAuthentication(AppAuthentication):
    def authenticate(  # type: ignore
        self, request: HttpRequest, username: str, password: str
    ) -> ChatAuthenticationSchema | None:
        user = super().authenticate(request, username, password)
        if user is None:
            return None

        chat = Chat.objects.get(platform_chat_id=request.headers.get("X-Chat-ID", ""))

        request.chat = chat

        return ChatAuthenticationSchema(
            api_user=user,
            chat=chat,
            chat_id=chat.platform_chat_id,
        )
