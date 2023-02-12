"""Module of various operations"""

from ontu_parser.classes import Parser
from ontu_parser.classes.dataclasses import Faculty, Group

from admin_site_database import models


def fetch_faculties() -> list[Faculty]:
    faculties = Parser().get_faculties()
    return faculties

def fetch_groups(faculty_entities: list[models.Faculty]) -> dict[models.Faculty, list[Group]]:
    parser = Parser()
    faculties: list[Faculty] = parser.get_faculties()
    groups_per_faculty: dict[str, list[Group]] = {}
    for faculty in faculties:
        faculty_id = None
        for entity in faculty_entities:
            if faculty.get_faculty_name() == entity.name:
                faculty_id = faculty.get_faculty_id()
                break
        else:
            continue

        groups = parser.get_groups(faculty_id=faculty_id)
        groups_per_faculty[entity] = groups
    return groups_per_faculty
