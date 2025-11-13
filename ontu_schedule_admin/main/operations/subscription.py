from typing import TYPE_CHECKING

from ontu_schedule_admin.api.schemas.department import Department
from ontu_schedule_admin.api.schemas.faculty import Faculty
from ontu_schedule_admin.api.schemas.grop import Group
from ontu_schedule_admin.api.schemas.subscription import Subscription as SubscriptionSchema
from ontu_schedule_admin.api.schemas.teacher import Teacher

from main.models.group import Group as GroupModel
from main.models.teacher import Teacher as TeacherModel

if TYPE_CHECKING:
    import pydantic

    from main.models.subscription import Subscription


def read_subscription_info(subscription: Subscription) -> SubscriptionSchema:
    return SubscriptionSchema(
        is_active=subscription.is_active,
        groups=[
            Group(
                uuid=group.uuid,
                short_name=group.short_name,
                faculty=Faculty(
                    uuid=group.faculty.uuid,
                    short_name=group.faculty.short_name,
                ),
            )
            for group in subscription.groups.all()
        ],
        teachers=[
            Teacher(
                uuid=teacher.uuid,
                short_name=teacher.short_name,
                full_name=teacher.full_name,
                departments=[
                    Department(
                        uuid=dept.uuid,
                        short_name=dept.short_name,
                        full_name=dept.full_name,
                    )
                    for dept in teacher.departments.all()
                ],
            )
            for teacher in subscription.teachers.all()
        ],
    )


def add_group_to_subscription(
    subscription: Subscription,
    group_id: pydantic.UUID4,
) -> Subscription:
    """Add a group to the subscription if it's not already present."""
    group = GroupModel.objects.get(uuid=group_id)

    if not subscription.groups.filter(uuid=group.uuid).exists():
        subscription.groups.add(group)

    return subscription


def remove_group_from_subscription(
    subscription: Subscription,
    group_id: pydantic.UUID4,
) -> Subscription:
    """Remove a group from the subscription if present.

    If the group is not attached to the subscription, this is a no-op.
    """
    try:
        group = GroupModel.objects.get(uuid=group_id)
    except GroupModel.DoesNotExist:
        # Let it raise to surface a 404 at the API layer similar to read operations
        raise

    if subscription.groups.filter(uuid=group.uuid).exists():
        subscription.groups.remove(group)

    return subscription


def add_teacher_to_subscription(
    subscription: Subscription,
    teacher_id: pydantic.UUID4,
) -> Subscription:
    """Add a teacher to the subscription if it's not already present."""
    teacher = TeacherModel.objects.get(uuid=teacher_id)

    if not subscription.teachers.filter(uuid=teacher.uuid).exists():
        subscription.teachers.add(teacher)

    return subscription


def remove_teacher_from_subscription(
    subscription: Subscription,
    teacher_id: pydantic.UUID4,
) -> Subscription:
    """Remove a teacher from the subscription if present.

    If the teacher is not attached to the subscription, this is a no-op.
    """
    try:
        teacher = TeacherModel.objects.get(uuid=teacher_id)
    except TeacherModel.DoesNotExist:
        # Surface 404-like error to the API layer
        raise

    if subscription.teachers.filter(uuid=teacher.uuid).exists():
        subscription.teachers.remove(teacher)

    return subscription


def update_subscription_status(subscription: Subscription) -> Subscription:
    """Toggle the subscription's active status and persist the change."""
    subscription.is_active = not subscription.is_active

    subscription.save(update_fields=["is_active", "updated_at"])

    return subscription
