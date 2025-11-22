import pydantic  # noqa: TC002
from django.core.paginator import Paginator
from django.http import HttpRequest  # noqa: TC002
from main.models.group import Group
from ninja import Query, Router

from ontu_schedule_admin.api.schemas.base import Meta
from ontu_schedule_admin.api.schemas.grop import (
    Group as GroupSchema,
)
from ontu_schedule_admin.api.schemas.grop import (
    GroupPaginatedRequest,
    GroupPaginatedResponse,
)
from ontu_schedule_admin.api.serializers.group import GroupSerializer

from .router import public_router

groups_router = Router(
    tags=[*(public_router.tags or []), "Group"],
)


@groups_router.get("/", response=GroupPaginatedResponse)
def read_groups(
    request: HttpRequest,  # noqa: ARG001
    query: Query[GroupPaginatedRequest],
) -> GroupPaginatedResponse:
    qs = Group.objects.order_by(
        "short_name",
    )

    if query.faculty_id:
        qs = qs.filter(
            faculty__uuid=query.faculty_id,
        )
    if query.name:
        qs = qs.filter(
            short_name__icontains=query.name,
        )

    paginator = Paginator(
        qs,
        per_page=query.page_size or 10,
        allow_empty_first_page=True,
    )

    page = paginator.get_page(query.page)
    return GroupPaginatedResponse(
        items=GroupSerializer(
            page.object_list,
            many=True,
        ).data,  # type: ignore
        meta=Meta(
            total=paginator.count,
            page=query.page,
            page_size=query.page_size or 10,
            has_next=page.has_next(),
            has_previous=page.has_previous(),
        ),
    )


@groups_router.get("/{group_id}", response=GroupSchema)
def read_group(
    request: HttpRequest,  # noqa: ARG001
    group_id: pydantic.UUID4,
) -> GroupSchema:
    return GroupSchema.model_validate(
        GroupSerializer(
            Group.objects.get(
                uuid=group_id,
            ),
        ).data
    )


public_router.add_router("/group", groups_router)
