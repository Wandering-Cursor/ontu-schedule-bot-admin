from django.views.decorators.csrf import ensure_csrf_cookie
from ninja import Router
from ninja.security import django_auth

admin_router = Router(
    auth=django_auth,
    tags=[
        "Admin",
    ],
)

admin_router.add_decorator(ensure_csrf_cookie, mode="view")
