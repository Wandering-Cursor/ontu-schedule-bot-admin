from typing import TypeVar

import pydantic
from ninja import Schema as APISchema
from ninja.pagination import PageNumberPagination

T = TypeVar("T", bound=APISchema)


class Schema(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(
        from_attributes=True,
    )


class Meta(APISchema):
    total: int
    page: int
    page_size: int

    has_next: bool = False
    has_previous: bool = False


class PaginatedRequest(PageNumberPagination.Input):
    pass


class PaginatedResponse[T](APISchema):
    meta: Meta
    items: list[T]
