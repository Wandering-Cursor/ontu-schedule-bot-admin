from django.core.management.base import BaseCommand

from admin_site_database.model_files.department import Department
from admin_site_database.model_files.teacher import Teacher
from admin_site_database.operations import get_teachers_by_department


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        departments = [x.external_id for x in Department.objects.all()]

        for department_id in departments:
            teachers = get_teachers_by_department(
                department_id=department_id,
            )

            for teacher in teachers:
                names = teacher.get_teacher_name()
                defaults = {
                    "short_name": names["short"],
                    "full_name": names["full"],
                    "department": Department.objects.filter(
                        external_id=department_id,
                    ).first(),
                }
                entity, created = Teacher.objects.update_or_create(
                    external_id=teacher.get_teacher_id(),
                    defaults=defaults,
                )

                if defaults["department"] not in entity.departments.all():
                    entity.departments.add(defaults["department"])
                    entity.save()

                self.stdout.write(f"Teacher: {entity=} created (or updated): {created=}")

        self.stdout.write(self.style.SUCCESS("Successfully loaded teachers"))
