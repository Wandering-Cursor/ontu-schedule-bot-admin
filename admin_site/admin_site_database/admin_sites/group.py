"""
Admin Site for ONTU Groups.
"""
from admin_site_database.admin_sites.base import BaseAdmin
from admin_site_database.model_files import Group
from django.contrib import admin


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    """
    Group Admin Site. Allows to see Groups of faculties
    """
    list_display = BaseAdmin.list_display + [
        'name',
        'faculty'
    ]

    list_filter = ['faculty']
