from django.contrib.admin import register
from django.contrib.auth.admin import UserAdmin

from main.models.api_user import APIUser


@register(APIUser)
class APIUserAdmin(UserAdmin):
    # Override UserAdmin defaults that reference non-existent fields
    filter_horizontal = ()
    list_filter = ()

    list_display = (
        "uuid",
        "username",
        "created_at",
        "updated_at",
    )

    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
        "last_login",
    )

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Metadata", {"fields": ("uuid", "created_at", "updated_at", "last_login")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )

    ordering = ("-created_at",)
