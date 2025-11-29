import hashlib
from typing import TYPE_CHECKING

from django.core.cache import cache
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
        timer = timezone.now()
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

        make_log(
            {
                "msg": "ChatAuthentication: User found",
                "time_taken_ms": (timezone.now() - timer).total_seconds() * 1000,
            }
        )

        # Fast-path: cache successful password checks for 30 seconds
        pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        cache_key_pw = f"auth:pw_ok:{username}:{pw_hash}"
        pw_ok = cache.get(cache_key_pw)
        if pw_ok is True:
            pass
        elif not user.check_password(password):
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
        else:
            # Cache success to avoid repeated expensive PBKDF2 checks
            cache.set(cache_key_pw, True, timeout=30)  # noqa: FBT003

        make_log(
            {
                "msg": "ChatAuthentication: User authenticated successfully",
                "username": username,
                "time_taken_ms": (timezone.now() - timer).total_seconds() * 1000,
            }
        )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        make_log(
            {
                "msg": "ChatAuthentication: User last_login updated",
                "username": username,
                "time_taken_ms": (timezone.now() - timer).total_seconds() * 1000,
            }
        )

        return user


class ChatAuthentication(AppAuthentication):
    def authenticate(  # type: ignore
        self, request: HttpRequest, username: str, password: str
    ) -> ChatAuthenticationSchema | None:
        timer = timezone.now()
        user = super().authenticate(request, username, password)
        if user is None:
            return None
        make_log(
            {
                "msg": "ChatAuthentication: Super authentication successful",
                "username": username,
                "time_taken_ms": (timezone.now() - timer).total_seconds() * 1000,
            }
        )

        chat = Chat.objects.get(platform_chat_id=request.headers.get("X-Chat-ID", ""))

        make_log(
            {
                "msg": "ChatAuthentication: Chat found",
                "platform_chat_id": chat.platform_chat_id,
                "time_taken_ms": (timezone.now() - timer).total_seconds() * 1000,
            }
        )

        request.chat = chat  # pyright: ignore[reportAttributeAccessIssue]

        return ChatAuthenticationSchema(
            api_user=user,
            chat=chat,
            chat_id=chat.platform_chat_id,
        )
