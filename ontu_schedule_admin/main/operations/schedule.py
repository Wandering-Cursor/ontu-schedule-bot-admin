from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main.models.group import Group

from main.operations.third_party.schedule_api import (
    get_schedule_by_group as api_get_schedule_by_group,
)


def get_schedule_by_group(
    group: Group,
) -> dict:
    return api_get_schedule_by_group(group=group)
