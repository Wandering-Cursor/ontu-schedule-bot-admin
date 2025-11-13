import pydantic
from main.models.api_user import APIUser  # noqa: TC002
from main.models.chat import Chat  # noqa: TC002

from ontu_schedule_admin.api.schemas.base import Schema


class ChatAuthenticationSchema(Schema):
    api_user: APIUser
    chat_id: str
    chat: Chat

    model_config = pydantic.ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True,
    )
