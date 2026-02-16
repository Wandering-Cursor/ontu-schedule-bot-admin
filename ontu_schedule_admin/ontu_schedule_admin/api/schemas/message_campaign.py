import datetime  # noqa: TC003

import pydantic

from ontu_schedule_admin.api.schemas.base import PaginatedRequest, PaginatedResponse, Schema
from ontu_schedule_admin.api.schemas.chat import Chat  # noqa: TC001


class MessageCampaignPaginatedRequest(PaginatedRequest):
    name: str | None = pydantic.Field(
        default=None,
        description='"Contains" search in the name of the campaign',
    )


class MessageCampaign(Schema):
    uuid: pydantic.UUID4

    name: str
    payload: pydantic.JsonValue
    recipients: list[Chat]

    created_at: datetime.datetime


class MessageCampaignPaginatedResponse(PaginatedResponse[MessageCampaign]):
    pass
