from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpRequest  # noqa: TC002
from main.models.message_campaign import MessageCampaign
from ninja import Query, Router
from ninja.errors import HttpError
from ninja.params.functions import Header as HeaderF
from pydantic import UUID4  # noqa: TC002

from ontu_schedule_admin.api.auth import AppAuthentication, ChatAuthentication
from ontu_schedule_admin.api.schemas.base import Meta
from ontu_schedule_admin.api.schemas.message_campaign import (
    MessageCampaign as MessageCampaignSchema,
)
from ontu_schedule_admin.api.schemas.message_campaign import (
    MessageCampaignPaginatedRequest,
    MessageCampaignPaginatedResponse,
)
from ontu_schedule_admin.api.serializers.message_campaign import MessageCampaignSerializer

from .router import chat_router

message_campaign_router = Router(
    tags=(chat_router.tags or [])
    + [
        "Message Campaign",
    ],
    auth=[AppAuthentication(), ChatAuthentication()],
)


@message_campaign_router.get(
    path="/",
    response=MessageCampaignPaginatedResponse,
)
@transaction.atomic
def list_message_campaigns(
    request: HttpRequest,  # noqa: ARG001
    query: Query[MessageCampaignPaginatedRequest],
    chat_id: str | None = HeaderF(
        alias="X-Chat-ID",
        default=None,
    ),
) -> MessageCampaignPaginatedResponse:
    qs = MessageCampaign.objects.order_by(
        "-created_at",
    )

    if query.name:
        qs = qs.filter(
            full_name__icontains=query.name,
        )

    if chat_id:
        qs = qs.filter(
            recipients__platform_chat_id=chat_id,
        )

    paginator = Paginator(
        qs,
        per_page=query.page_size or 10,
        allow_empty_first_page=True,
    )

    page = paginator.get_page(query.page)
    return MessageCampaignPaginatedResponse(
        items=MessageCampaignSerializer(
            page.object_list,
            many=True,
            context={"X-Chat-ID": chat_id},
        ).data,  # type: ignore
        meta=Meta(
            total=paginator.count,
            page=query.page,
            page_size=query.page_size or 10,
            has_next=page.has_next(),
            has_previous=page.has_previous(),
        ),
    )


@message_campaign_router.get(
    path="/{message_campaign_id}",
    response=MessageCampaignSchema,
)
@transaction.atomic
def get_message_campaign(
    request: HttpRequest,  # noqa: ARG001
    message_campaign_id: UUID4,
    chat_id: str | None = HeaderF(
        alias="X-Chat-ID",
        default=None,
    ),
) -> MessageCampaignSchema:
    try:
        qs = MessageCampaign.objects.filter(
            uuid=message_campaign_id,
        )

        if chat_id:
            qs = qs.filter(
                recipients__platform_chat_id=chat_id,
            )

        campaign = qs.get()
    except MessageCampaign.DoesNotExist as e:
        raise HttpError(404, message="Message Campaign not found.") from e
    return MessageCampaignSchema.model_validate(
        MessageCampaignSerializer(
            campaign,
            context={
                "X-Chat-ID": chat_id,
            },
        ).data,
    )


chat_router.add_router("/message_campaign", message_campaign_router)
