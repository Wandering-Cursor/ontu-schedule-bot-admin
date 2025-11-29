import hashlib
import hmac
from typing import TYPE_CHECKING

from django.conf import settings
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

        # Fast-path: cache successful password checks for 30 seconds
        # Use HMAC-SHA256 with SECRET_KEY for password hash in cache key
        password_hash = hmac.new(
            settings.SECRET_KEY.encode(),
            password.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        cache_key_password_check = f"auth:pw_ok:{username}:{password_hash}"
        password_checked = cache.get(cache_key_password_check)
        if password_checked is True:
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
            cache.set(cache_key_password_check, True, timeout=30)  # noqa: FBT003

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

        request.chat = chat  # pyright: ignore[reportAttributeAccessIssue]

        return ChatAuthenticationSchema(
            api_user=user,
            chat=chat,
            chat_id=chat.platform_chat_id,
        )
