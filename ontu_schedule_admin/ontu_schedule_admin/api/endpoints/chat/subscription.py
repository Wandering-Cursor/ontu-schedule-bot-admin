"""
Allows to manage subscription for authenticated (via chat) users.

Enable/disable and add/remove groups/teachers to/from subscription.
"""

from typing import TYPE_CHECKING

import pydantic  # noqa: TC002
from django.http import HttpRequest  # noqa: TC002
from main.operations import subscription as subscription_ops
from ninja import Router
from ninja.errors import HttpError
from ninja.params.functions import Header

from ontu_schedule_admin.api.auth import ChatAuthentication
from ontu_schedule_admin.api.schemas.subscription import Subscription

from .router import chat_router

if TYPE_CHECKING:
    from ontu_schedule_admin.api.schemas.auth import ChatAuthenticationSchema

subscription_router = Router(
    tags=(chat_router.tags or [])
    + [
        "Subscription",
    ],
    auth=ChatAuthentication(),
)


@subscription_router.post(
    "/",
    response=Subscription,
)
def create_subscription(
    request: HttpRequest,
    chat_id: str = Header(alias="X-Chat-ID"),  # noqa: ARG001
) -> Subscription:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    if auth.chat.subscription:
        raise HttpError(400, message="Chat already has a subscription.")

    subscription = subscription_ops.create_subscription(
        chat=auth.chat,
    )

    return subscription_ops.read_subscription_info(subscription)


@subscription_router.get(
    "/info",
    response=Subscription,
)
def read_subscription_info(
    request: HttpRequest,
    chat_id: str = Header(alias="X-Chat-ID"),  # noqa: ARG001
) -> Subscription:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    subscription = auth.chat.subscription

    if not subscription:
        raise HttpError(404, message="Chat doesn't have a subscription.")

    return subscription_ops.read_subscription_info(
        subscription=subscription,
    )


@subscription_router.post(
    "/info/group/{group_id}",
    response=Subscription,
)
def add_group_to_subscription(
    request: HttpRequest,
    group_id: pydantic.UUID4,
    chat_id: str = Header(alias="X-Chat-ID"),  # noqa: ARG001
) -> Subscription:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    subscription = auth.chat.subscription

    if not subscription:
        raise HttpError(404, message="Chat doesn't have a subscription.")

    subscription = subscription_ops.add_group_to_subscription(
        subscription=subscription,
        group_id=group_id,
    )

    return subscription_ops.read_subscription_info(subscription)


@subscription_router.delete(
    "/info/group/{group_id}",
    response=Subscription,
)
def remove_group_from_subscription(
    request: HttpRequest,
    group_id: pydantic.UUID4,
    chat_id: str = Header(alias="X-Chat-ID"),  # noqa: ARG001
) -> Subscription:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    subscription = auth.chat.subscription

    if not subscription:
        raise HttpError(404, message="Chat doesn't have a subscription.")

    subscription = subscription_ops.remove_group_from_subscription(
        subscription=subscription,
        group_id=group_id,
    )

    return subscription_ops.read_subscription_info(subscription)


@subscription_router.post(
    "/info/teacher/{teacher_id}",
    response=Subscription,
)
def add_teacher_to_subscription(
    request: HttpRequest,
    teacher_id: pydantic.UUID4,
    chat_id: str = Header(alias="X-Chat-ID"),  # noqa: ARG001
) -> Subscription:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    subscription = auth.chat.subscription

    if not subscription:
        raise HttpError(404, message="Chat doesn't have a subscription.")

    subscription = subscription_ops.add_teacher_to_subscription(
        subscription=subscription,
        teacher_id=teacher_id,
    )

    return subscription_ops.read_subscription_info(subscription)


@subscription_router.delete(
    "/info/teacher/{teacher_id}",
    response=Subscription,
)
def remove_teacher_from_subscription(
    request: HttpRequest,
    teacher_id: pydantic.UUID4,
    chat_id: str = Header(alias="X-Chat-ID"),  # noqa: ARG001
) -> Subscription:
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    subscription = auth.chat.subscription

    if not subscription:
        raise HttpError(404, message="Chat doesn't have a subscription.")

    subscription = subscription_ops.remove_teacher_from_subscription(
        subscription=subscription,
        teacher_id=teacher_id,
    )

    return subscription_ops.read_subscription_info(subscription)


@subscription_router.patch(
    "/status",
    response=Subscription,
)
def update_subscription_status(
    request: HttpRequest,
    chat_id: str = Header(alias="X-Chat-ID"),  # noqa: ARG001
) -> Subscription:
    """Toggles subscription status (is_active field)."""
    auth: ChatAuthenticationSchema = getattr(request, "auth", None)  # pyright: ignore[reportAssignmentType]

    subscription = auth.chat.subscription

    if not subscription:
        raise HttpError(404, message="Chat doesn't have a subscription.")

    subscription = subscription_ops.update_subscription_status(
        subscription=subscription,
    )

    return subscription_ops.read_subscription_info(subscription)


chat_router.add_router("/subscription", subscription_router)
