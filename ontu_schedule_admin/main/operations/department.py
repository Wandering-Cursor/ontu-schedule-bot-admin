from ontu_schedule_admin.api.utils.log import make_log

from main.models.department import Department

from .third_party.schedule_api import get_departments


def update_departments_from_api() -> None:
    api_departments = get_departments()

    make_log(
        {
            "msg": f"Got {len(api_departments)} departments from Schedule API",
        },
        level="INFO",
    )

    for api_department in api_departments:
        department_names = api_department.get_department_name()

        Department.objects.update_or_create(
            external_id=api_department.get_department_id(),
            defaults={
                "short_name": department_names["short"],
                "full_name": department_names["full"],
            },
        )
