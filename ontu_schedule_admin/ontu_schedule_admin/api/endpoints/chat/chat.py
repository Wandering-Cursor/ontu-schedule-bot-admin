from django.http import HttpRequest  # noqa: TC002
from main.models.chat import Chat
from main.operations import subscription as subscription_ops
from ninja.errors import HttpError

from ontu_schedule_admin.api.schemas.chat import Chat as ChatSchema
from ontu_schedule_admin.api.schemas.chat import CreateChatRequest
from ontu_schedule_admin.api.serializers.chat import ChatSerializer

from .router import chat_router


@chat_router.post("/", response=ChatSchema)
def create_chat(
    request: HttpRequest,  # noqa: ARG001
    body: CreateChatRequest,
) -> ChatSchema:
    """
    Create a chat entry in the system.
    """
    chat, created = Chat.objects.get_or_create(
        platform=body.platform,
        platform_chat_id=body.platform_chat_id,
        defaults={
            "title": body.title,
            "username": body.username,
            "first_name": body.first_name,
            "last_name": body.last_name,
            "language_code": body.language_code,
            "additional_info": body.additional_info,
        },
    )

    if created:
        chat.subscription = subscription_ops.create_subscription(chat=chat)
        chat.save()

    return ChatSchema.model_validate(ChatSerializer(chat).data)


@chat_router.get("/{chat_id}", response=ChatSchema)
def read_chat(
    request: HttpRequest,  # noqa: ARG001
    chat_id: str,
) -> ChatSchema:
    """
    Read chat information by chat ID.
    """
    try:
        chat = Chat.objects.get(platform_chat_id=chat_id)
    except Chat.DoesNotExist as e:
        raise HttpError(404, message="Chat not found.") from e

    return ChatSchema.model_validate(ChatSerializer(chat).data)
