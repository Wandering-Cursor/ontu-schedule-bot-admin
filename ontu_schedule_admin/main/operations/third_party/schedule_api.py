from typing import TYPE_CHECKING

from ontu_parser.classes import Parser
from ontu_schedule_admin.api.utils.log import make_log

if TYPE_CHECKING:
    from ontu_parser.classes.dataclasses import Department as ParserDepartment
    from ontu_parser.classes.dataclasses import Faculty as ParserFaculty
    from ontu_parser.classes.dataclasses import Group as ParserGroup
    from ontu_parser.classes.dataclasses import StudentsPair, TeachersPair
    from ontu_parser.classes.dataclasses import Teacher as ParseTeacher

    from main.models.group import Group

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


def get_group(group: Group) -> ParserGroup | None:
    groups = get_groups(faculty_name=group.faculty.short_name)
    for parser_group in groups:
        if parser_group.get_group_name() == group.short_name:
            return parser_group
    return None


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


def get_schedule_by_group(
    group: Group,
) -> dict[str, list[StudentsPair | TeachersPair]]:
    api_group = get_group(group)

    if not api_group:
        raise ValueError(
            f"Group {group.short_name} not found in faculty {group.faculty.short_name}"
        )

    return global_parser.get_schedule(
        group_id=int(api_group.get_group_id()),  # pyright: ignore[reportArgumentType]
    )
