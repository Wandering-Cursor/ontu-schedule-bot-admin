from django.core.management.base import BaseCommand

from admin_site_database.model_files.faculty import Faculty
from admin_site_database.operations import fetch_faculties


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        faculties = fetch_faculties()

        for faculty in faculties:
            new_faculty, created = Faculty.objects.get_or_create(
                name=faculty.get_faculty_name(),
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created Faculty: {new_faculty}"))
                new_faculty.save()

        self.stdout.write(self.style.SUCCESS("Successfully loaded faculties"))
