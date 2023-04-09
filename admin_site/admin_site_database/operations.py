"""Module of various operations"""

from ontu_parser.classes import Parser
from ontu_parser.classes.dataclasses import Faculty, Group, BaseLesson

from admin_site_database.model_files import Faculty as model_Faculty


global_parser = Parser()


def fetch_faculties() -> list[Faculty]:
    faculties = global_parser.get_faculties()
    return faculties


def fetch_groups(faculty_entities: list[model_Faculty]) -> dict[model_Faculty, list[Group]]:
    faculties: list[Faculty] = global_parser.get_faculties()
    groups_per_faculty: dict[str, list[Group]] = {}
    for faculty in faculties:
        faculty_id = None
        for entity in faculty_entities:
            if faculty.get_faculty_name() == entity.name:
                faculty_id = faculty.get_faculty_id()
                break
        else:
            continue

        groups = global_parser.get_groups(faculty_id=faculty_id)
        groups_per_faculty[entity] = groups
    return groups_per_faculty


def fetch_schedule(faculty_name: str, group_name: str):
    faculty_id: int | None = None
    group_id: int | None = None

    schedule: dict | None = None

    faculties = global_parser.get_faculties()
    for faculty in faculties:
        if faculty.get_faculty_name() == faculty_name:
            faculty_id = faculty.get_faculty_id()
            break
    else:
        raise ValueError("Could not get faculty by name", faculty_name, faculties)

    groups = global_parser.get_groups(faculty_id=faculty_id)
    for group in groups:
        if group.get_group_name() == group_name:
            group_id = group.get_group_id()
            break
    else:
        raise ValueError("Could not get group by name", faculty_name, group_name, groups)

    schedule = global_parser.get_schedule(group_id=group_id)
    result = {"days": {}}

    for day_name, pairs in schedule.items():
        pairs_per_day = []
        for pair in pairs:
            converted_lessons = []
            for lesson in pair.lessons:
                converted_lessons.append(_convert_lesson(lesson))
            data = {
                "lessons": converted_lessons,
                "pair_no": pair.pair_no,
            }
            pairs_per_day.append(
                data
            )
        result["days"][day_name] = pairs_per_day

    return result


def _convert_lesson(lesson: BaseLesson):
    return {
        "date": lesson.lesson_date,
        "teacher": {
            "full_name": lesson.teacher["full"],
            "short_name": lesson.teacher["short"],
        },
        "lesson_name": {
            "full_name": lesson.lesson_name["full"],
            "short_name": lesson.lesson_name["short"],
        },
        "lesson_info": lesson.lesson_info,
        "auditorium": lesson.auditorium,
    }
