import pydantic  # noqa: TC002
from django.core.paginator import Paginator
from django.http import HttpRequest  # noqa: TC002
from main.models.faculty import Faculty
from ninja import Query, Router

from ontu_schedule_admin.api.schemas.base import Meta
from ontu_schedule_admin.api.schemas.faculty import (
    Faculty as FacultySchema,
)
from ontu_schedule_admin.api.schemas.faculty import (
    FacultyPaginatedRequest,
    FacultyPaginatedResponse,
)
from ontu_schedule_admin.api.serializers.faculty import FacultySerializer

from .router import public_router

faculties_router = Router(
    tags=[*(public_router.tags or []), "Faculty"],
)


@faculties_router.get("/", response=FacultyPaginatedResponse)
def read_faculties(
    request: HttpRequest,  # noqa: ARG001
    query: Query[FacultyPaginatedRequest],
) -> FacultyPaginatedResponse:
    qs = Faculty.objects.order_by(
        "short_name",
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
    return FacultyPaginatedResponse(
        items=FacultySerializer(
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


@faculties_router.get("/{faculty_id}", response=FacultySchema)
def read_faculty(
    request: HttpRequest,  # noqa: ARG001
    faculty_id: pydantic.UUID4,
) -> FacultySchema:
    return FacultySchema.model_validate(
        FacultySerializer(
            Faculty.objects.get(
                uuid=faculty_id,
            ),
        ).data
    )


public_router.add_router("/faculty", faculties_router)
