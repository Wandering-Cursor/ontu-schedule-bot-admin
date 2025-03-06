from django.core.management.base import BaseCommand

from admin_site_database.model_files.faculty import Faculty
from admin_site_database.model_files.group import Group
from admin_site_database.operations import fetch_groups


class Command(BaseCommand):
    def handle(self, *args, **options) -> None:  # noqa: ANN002, ANN003, ARG002
        faculties = list(Faculty.objects.all())
        groups_per_faculty = fetch_groups(faculties)

        for faculty, groups in groups_per_faculty.items():
            faculty: Faculty
            self.stdout.write(self.style.SUCCESS(f"Now fetching faculty: {faculty}"))
            for group in groups:
                group_name = group.get_group_name()
                new_group, created = Group.objects.get_or_create(
                    faculty_id=faculty.id, name=group_name
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created Group: {new_group}"))
                    new_group.save()

        self.stdout.write(self.style.SUCCESS("Successfully loaded groups"))
