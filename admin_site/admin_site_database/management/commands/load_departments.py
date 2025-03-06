from django.core.management.base import BaseCommand

from admin_site_database.model_files.department import Department
from admin_site_database.operations import get_departments


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        current_departments = get_departments()
        for department in current_departments:
            names = department.get_department_name()

            defaults = {
                "short_name": names["short"],
                "full_name": names["full"],
            }

            entity, created = Department.objects.update_or_create(
                external_id=department.get_department_id(),
                defaults=defaults,
            )
            if created:
                self.stdout.write(f"Department: {entity=} created")
                entity.save()

        self.stdout.write(self.style.SUCCESS("Successfully loaded departments"))
