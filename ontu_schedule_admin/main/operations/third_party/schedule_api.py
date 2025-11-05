from typing import TYPE_CHECKING

from ontu_parser.classes import Parser
from ontu_schedule_admin.api.utils.log import make_log

if TYPE_CHECKING:
    from ontu_parser.classes.dataclasses import Department as ParserDepartment
    from ontu_parser.classes.dataclasses import Faculty as ParserFaculty
    from ontu_parser.classes.dataclasses import Group as ParserGroup
    from ontu_parser.classes.dataclasses import Teacher as ParseTeacher

global_parser = Parser()
global_teacher_parser = Parser(kwargs={"for_teachers": True})


def get_faculties() -> list[ParserFaculty]:
    faculties = global_parser.get_faculties()
    faculties += global_parser.get_all_extramurals()
    return faculties


def get_faculty_by_name(faculty_name: str) -> ParserFaculty | None:
    faculties = global_parser.get_faculties()
    for faculty in faculties:
        if faculty.get_faculty_name() == faculty_name:
            return faculty
    return None


def get_departments() -> list[ParserDepartment]:
    return global_teacher_parser.get_departments()


def get_groups(faculty_name: str) -> list[ParserGroup]:
    faculty = get_faculty_by_name(faculty_name)

    if faculty is None:
        make_log(
            {
                "msg": f"Faculty with name {faculty_name} not found",
            },
            level="ERROR",
        )
        return []

    return global_parser.get_groups(
        faculty=faculty,
    )


def get_teachers(department_external_id: str) -> list[ParseTeacher]:
    return global_teacher_parser.get_teachers_by_department(
        department_id=int(department_external_id),
    )
