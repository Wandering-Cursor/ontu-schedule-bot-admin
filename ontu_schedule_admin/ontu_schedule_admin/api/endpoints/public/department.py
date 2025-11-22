import pydantic  # noqa: TC002
from django.core.paginator import Paginator
from django.http import HttpRequest  # noqa: TC002
from main.models.department import Department
from ninja import Query, Router

from ontu_schedule_admin.api.schemas.base import Meta
from ontu_schedule_admin.api.schemas.department import (
    Department as DepartmentSchema,
)
from ontu_schedule_admin.api.schemas.department import (
    DepartmentPaginatedRequest,
    DepartmentPaginatedResponse,
)
from ontu_schedule_admin.api.serializers.department import DepartmentSerializer

from .router import public_router

departments_router = Router(
    tags=[*(public_router.tags or []), "Department"],
)


@departments_router.get("/", response=DepartmentPaginatedResponse)
def read_departments(
    request: HttpRequest,  # noqa: ARG001
    query: Query[DepartmentPaginatedRequest],
) -> DepartmentPaginatedResponse:
    qs = Department.objects.order_by(
        "short_name",
    )

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
    return DepartmentPaginatedResponse(
        items=DepartmentSerializer(
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


@departments_router.get("/{department_id}", response=DepartmentSchema)
def read_department(
    request: HttpRequest,  # noqa: ARG001
    department_id: pydantic.UUID4,
) -> DepartmentSchema:
    return DepartmentSchema.model_validate(
        DepartmentSerializer(
            Department.objects.get(
                uuid=department_id,
            ),
        ).data
    )


public_router.add_router("/department", departments_router)
