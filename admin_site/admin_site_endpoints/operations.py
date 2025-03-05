from .models import ScheduleCache


def reset_cache(faculty_name: str, group_name: str) -> tuple[int, dict[str, int]]:
    return ScheduleCache.objects.filter(
        faculty=faculty_name,
        group=group_name,
    ).delete()
