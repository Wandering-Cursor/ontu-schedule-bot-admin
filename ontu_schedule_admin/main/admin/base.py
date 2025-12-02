from typing import TYPE_CHECKING

from django.contrib.admin import ModelAdmin
from djangoql.admin import DjangoQLSearchMixin

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from django.http import HttpRequest


class BaseModelAdmin(DjangoQLSearchMixin, ModelAdmin):
    readonly_fields: tuple = (  # type: ignore
        "uuid",
        "created_at",
        "updated_at",
    )

    list_display = (
        "uuid",
        "created_at",
        "updated_at",
    )

    ADD_DEFAULT_FIELDS: bool = True
    DEFAULT_FIELDS = (
        "uuid",
        "created_at",
        "updated_at",
    )

    fields_override = ()
    list_display_extra = ()

    def get_list_display(
        self,
        request: HttpRequest,  # noqa: ARG002
    ) -> tuple:
        return (
            *self.list_display[:1],
            *self.list_display_extra,
            *self.list_display[1:],
        )

    def get_fields(
        self,
        request: HttpRequest,
        obj: object | None = None,
    ) -> Sequence[Callable[..., object] | str]:
        if self.fields_override and self.ADD_DEFAULT_FIELDS:
            return (
                *self.fields_override,
                *self.DEFAULT_FIELDS,
            )
        if self.fields_override:
            return (*self.fields_override,)
        fields = super().get_fields(request, obj)
        # Remove default fields and add uuid as first, dates as last
        fields = tuple([field for field in fields if field not in self.DEFAULT_FIELDS])
        return (
            "uuid",
            *fields,
            "created_at",
            "updated_at",
        )
