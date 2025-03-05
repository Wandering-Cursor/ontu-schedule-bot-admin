"""
Admin Site for Faculty and actions.
"""

from django.contrib import admin
from django.db import transaction

from admin_site_database import operations
from admin_site_database.admin_sites.base import BaseAdmin
from admin_site_database.model_files import Faculty, Group


@admin.action(description="Update list of Faculties")
@transaction.atomic
def get_faculties(_, *args, **kwargs):
    """Action to fetch faculties"""
    faculties = operations.fetch_faculties()
    for faculty in faculties:
        new_faculty, created = Faculty.objects.get_or_create(
            name=faculty.get_faculty_name()
        )
        new_faculty: Faculty
        if created:
            new_faculty.save()


@admin.action(description="Fetch list of groups for selected faculties")
@transaction.atomic
def get_groups(_, __, queryset):
    """Action to fetch list of groups per Faculty

    Args:
        ...
        queryset (`Queryset[models.Faculty]`): Selected Faculties
    """
    faculties: list[Faculty] = queryset.all()
    groups_per_faculty = operations.fetch_groups(faculties)
    for faculty, groups in groups_per_faculty.items():
        faculty: Faculty
        print(f"Now fetching faculty: {faculty}")
        for group in groups:
            group_name = group.get_group_name()
            print(f"Fetching Group: {group_name}")
            new_group, created = Group.objects.get_or_create(
                faculty_id=faculty.id, name=group_name
            )
            new_group: Group
            if created:
                new_group.save()


@admin.register(Faculty)
class FacultyAdmin(BaseAdmin):
    """
    Faculty Admin Site. Displays Faculty models.

    Using Actions you can fetch Faculties and Groups
    """

    list_display = BaseAdmin.list_display + ["name"]
    fields = ["name"]

    actions = [get_faculties, get_groups]
