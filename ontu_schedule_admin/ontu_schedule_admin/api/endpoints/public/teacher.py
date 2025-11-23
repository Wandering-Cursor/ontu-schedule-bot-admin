import pydantic  # noqa: TC002
from django.core.paginator import Paginator
from django.http import HttpRequest  # noqa: TC002
from main.models.teacher import Teacher
from ninja import Query, Router
from ninja.errors import HttpError

from ontu_schedule_admin.api.schemas.base import Meta
from ontu_schedule_admin.api.schemas.teacher import (
    Teacher as TeacherSchema,
)
from ontu_schedule_admin.api.schemas.teacher import (
    TeacherPaginatedRequest,
    TeacherPaginatedResponse,
)
from ontu_schedule_admin.api.serializers.teacher import TeacherSerializer

from .router import public_router

teachers_router = Router(
    tags=[*(public_router.tags or []), "Teacher"],
)


@teachers_router.get("/", response=TeacherPaginatedResponse)
def read_teachers(
    request: HttpRequest,  # noqa: ARG001
    query: Query[TeacherPaginatedRequest],
) -> TeacherPaginatedResponse:
    qs = Teacher.objects.order_by(
        "short_name",
    )

    if query.department_id:
        qs = qs.filter(
            departments__uuid=query.department_id,
        ).distinct()
    if query.name:
        qs = qs.filter(
            full_name__icontains=query.name,
        )

    paginator = Paginator(
        qs,
        per_page=query.page_size or 10,
        allow_empty_first_page=True,
    )

    page = paginator.get_page(query.page)
    return TeacherPaginatedResponse(
        items=TeacherSerializer(
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


@teachers_router.get("/{teacher_id}", response=TeacherSchema)
def read_teacher(
    request: HttpRequest,  # noqa: ARG001
    teacher_id: pydantic.UUID4,
) -> TeacherSchema:
    try:
        teacher = Teacher.objects.get(uuid=teacher_id)
    except Teacher.DoesNotExist as e:
        raise HttpError(404, message="Teacher not found.") from e
    return TeacherSchema.model_validate(TeacherSerializer(teacher).data)


public_router.add_router("/teacher", teachers_router)
