"""Admin classes for database"""
from django.contrib import admin

from django.db import transaction

from admin_site_database import models

from admin_site_database import operations

class BaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'created', 'updated']

    readonly_fields = ['id', 'created', 'updated']


@admin.action(description="Update list of Faculties")
@transaction.atomic
def get_faculties(modeladmin, *args, **kwargs):
    faculties = operations.fetch_faculties()
    for faculty in faculties:
        new_faculty, created = models.Faculty.objects.get_or_create(
            name=faculty.get_faculty_name()
        )
        new_faculty: models.Faculty
        if created:
            new_faculty.save()


@admin.action(description="Fetch list of groups for selected faculties")
@transaction.atomic
def get_groups(modeladmin, request, queryset):
    faculties: list[models.Faculty] = queryset.all()
    groups_per_faculty = operations.fetch_groups(faculties)
    for faculty, groups in groups_per_faculty.items():
        faculty: models.Faculty
        print(f"Now fetching faculty: {faculty}")
        for group in groups:
            group_name = group.get_group_name()
            print(f"Fetching Group: {group_name}")
            new_group, created = models.Group.objects.get_or_create(
                faculty_id=faculty.id,
                name=group_name
            )
            new_group: models.Group
            if created:
                new_group.save()


@admin.register(models.Faculty)
class FacultyAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + [
        'name'
    ]
    fields = [
        'name'
    ]

    actions = [get_faculties, get_groups]


@admin.register(models.Group)
class GroupAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + [
        'name',
        'faculty'
    ]

    list_filter = ['faculty']


@admin.register(models.Subscription)
class SubscriptionAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + [
        'is_active',
        'group',
        'get_telegram_chats'
    ]

    def get_telegram_chats(self, obj: models.Subscription):
        return obj.related_telegram_chats


@admin.register(models.TelegramChat)
class TelegramChatAdmin(BaseAdmin):
    list_display = BaseAdmin.list_display + [
        'telegram_id',
        'name',
        'subscription',
        'chat_info'
    ]

    readonly_fields = BaseAdmin.readonly_fields + [
        'telegram_id',
        'chat_info'
    ]
