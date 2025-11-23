import pydantic
from main.enums import Platform  # noqa: TC002

from ontu_schedule_admin.api.schemas.base import Schema


class Chat(Schema):
    uuid: pydantic.UUID4

    platform: Platform

    platform_chat_id: str

    title: str | None
    username: str | None
    first_name: str | None
    last_name: str | None
    language_code: str | None
    additional_info: dict | None


class CreateChatRequest(Schema):
    platform: Platform

    platform_chat_id: str

    title: str | None = pydantic.Field(
        default=None,
        description="Title of the chat.",
    )
    username: str | None = pydantic.Field(
        default=None,
        description="Username of the chat.",
    )
    first_name: str | None = pydantic.Field(
        default=None,
        description="First name of the chat.",
    )
    last_name: str | None = pydantic.Field(
        default=None,
        description="Last name of the chat.",
    )
    language_code: str | None = pydantic.Field(
        default=None,
        description="Language code of the chat.",
    )
    additional_info: dict | None = pydantic.Field(
        default=None,
        description="Additional information about the chat.",
    )
