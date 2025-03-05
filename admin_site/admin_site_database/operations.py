"""Module of various operations"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ontu_parser.classes import Parser
from ontu_parser.classes.dataclasses import (
    BaseStudentsLesson,
    Faculty,
    Group,
    TeachersLesson,
)

from admin_site_database.model_files import Faculty as model_Faculty

from .decorators import do_until_success

if TYPE_CHECKING:
    from ontu_parser.classes.dataclasses import Teacher, TeachersLesson, TeachersPair

import logging

global_parser = Parser()
teachers_parser = Parser(kwargs={"for_teachers": True})


@do_until_success
def fetch_faculties() -> list[Faculty]:
    faculties = global_parser.get_faculties()
    return faculties


@do_until_success
def fetch_groups(
    faculty_entities: list[model_Faculty],
    *,
    fetch_extramural: bool = True,
) -> dict[model_Faculty, list[Group]]:
    faculties: list[Faculty] = global_parser.get_faculties()
    groups_per_faculty: dict[str, list[Group]] = {}
    for faculty in faculties:
        for entity in faculty_entities:
            if faculty.get_faculty_name() == entity.name:
                break
        else:
            continue

        groups = global_parser.get_groups(faculty=faculty)

        if fetch_extramural:
            extramural = global_parser.get_extramural(faculty.get_faculty_id())
            if extramural:
                groups += global_parser.get_groups(faculty=extramural)

        groups_per_faculty[entity] = groups
    return groups_per_faculty


@do_until_success
def get_schedule_by_group_id(group_id: int):
    logging.warning(
        f"Getting schedule with {group_id=}; {global_parser.sender.cookies.value=}"
    )
    schedule = global_parser.get_schedule(group_id=group_id)
    logging.warning(
        f"Post - got schedule {group_id=}; {global_parser.sender.cookies.value=}"
    )
    result = {"days": {}}

    for day_name, pairs in schedule.items():
        logging.warning(f"Day: {day_name=} - {pairs=}")
        pairs_per_day = []
        for pair in pairs:
            converted_lessons = []
            for lesson in pair.lessons:
                converted_lessons.append(_convert_lesson(lesson))
            data = {
                "lessons": converted_lessons,
                "pair_no": pair.pair_no,
            }
            pairs_per_day.append(data)
        result["days"][day_name] = pairs_per_day

    return result


def get_schedule_by_names(faculty_name: str, group_name: str):
    def __get_group_id(groups: list["Group"]) -> str | int:
        for group in groups:
            if group.get_group_name() == group_name:
                return group.get_group_id()

    faculty_id: int | None = None
    group_id: int | None = None

    faculties = global_parser.get_faculties()
    for faculty in faculties:
        if faculty.get_faculty_name() == faculty_name:
            faculty_id = faculty.get_faculty_id()
            break
    else:
        raise ValueError("Could not get faculty by name", faculty_name, faculties)

    groups = global_parser.get_groups(faculty_id=faculty_id)
    group_id = __get_group_id(groups=groups)
    if not group_id:
        extramural_faculty = global_parser.get_extramural(
            faculty_id=faculty.get_faculty_id()
        )
        if extramural_faculty:
            group_id = __get_group_id(
                groups=global_parser.get_groups(faculty=extramural_faculty)
            )

    if not group_id:
        raise ValueError(
            "Could not get group by name", faculty_name, group_name, groups
        )

    return get_schedule_by_group_id(group_id=group_id)


def get_departments():
    return teachers_parser.get_departments()


def get_teachers_by_department(department_id: str) -> "list[Teacher]":
    return teachers_parser.get_teachers_by_department(department_id=department_id)


def fetch_teacher_schedule(teacher_id: str):
    schedule = teachers_parser.get_schedule(teacher_id=teacher_id)
    result = {"days": {}}

    for day_name, pairs in schedule.items():
        pairs: "list[TeachersPair]"
        pairs_per_day = []
        for pair in pairs:
            pairs_per_day.append(
                {
                    "lesson": _convert_teachers_lesson(pair.lesson),
                    "pair_no": pair.pair_no,
                }
            )
        result["days"][day_name] = pairs_per_day

    return result


def _convert_lesson(lesson: BaseStudentsLesson):
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


def _convert_teachers_lesson(lesson: TeachersLesson | None):
    if not lesson:
        return {}

    return {
        "name": lesson.name,
        "groups": lesson.groups.split(", "),
    }
