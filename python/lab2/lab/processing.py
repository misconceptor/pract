"""Business logic: operations on a list of Student objects.

Every function is pure: it takes a list of students, returns a result,
and never prints or reads from stdin. I/O belongs to main.py.
"""

from __future__ import annotations

from typing import Iterable, List

from .errors import DuplicateIdError, StudentNotFoundError, ValidationError
from .models import Student, GRADE_MAX, GRADE_MIN, Grade

SortKey = str  # "avg" | "name" | "id"


def find_by_id(students: Iterable[Student], student_id: int) -> Student | None:
    """Return the student with the given id, or None."""
    for s in students:
        if s.id == student_id:
            return s
    return None

def find_by_name(students: Iterable[Student], name: str) -> List[Student]:
    """Return all students whose name contains `name` (case-insensitive)."""
    needle = name.strip().lower()
    if not needle:
        raise ValidationError("Search query must not be empty")
    return [s for s in students if needle in s.name.lower()]


def add_student(students: List[Student], student: Student) -> None:
    """Append a student in place. Raise if the id already exists."""
    if find_by_id(students, student.id) is not None:
        raise DuplicateIdError(f"Student with id={student.id} already exists")
    students.append(student)


def remove_student(students: List[Student], student_id: int) -> Student:
    """Remove and return the student. Raise if not found."""
    student = find_by_id(students, student_id)
    if student is None:
        raise StudentNotFoundError(f"No student with id={student_id}")
    students.remove(student)
    return student

def update_grades(students: List[Student], student_id: int, grades: List[int]) -> Student:
    """Replace the grades of a student. Raise if not found or invalid."""
    student = find_by_id(students, student_id)
    if student is None:
        raise StudentNotFoundError(f"No student with id={student_id}")
    # Validate through a temp instance so we don't corrupt on bad input
    validated = Student(student.id, student.name, list(grades))
    student.grades = validated.grades
    return student

def update_grade_at(students: List[Student], student_id: int, index: int, value: Grade) -> Student:
    """Set the grade at `index` (0-based). `value` may be None to clear.

    Extends the grade list with None slots if `index` is beyond the end.
    """
    if index < 0:
        raise ValidationError(f"Index must be >= 0, got {index}")

    student = find_by_id(students, student_id)
    if student is None:
        raise StudentNotFoundError(f"No student with id={student_id}")

    new_grades = list(student.grades)
    while len(new_grades) <= index:
        new_grades.append(None)
    new_grades[index] = value
    return update_grades(students, student_id, new_grades)

def remove_grade(students: List[Student], student_id: int, grade: int) -> Student:

    """Remove the first occurrence of `grade` from a student's grades."""
    if grade is None:
        raise ValidationError("Cannot remove None by value; use update_grade_at(..., None)")

    if not isinstance(grade, int) or isinstance(grade, bool):
        raise ValidationError(f"Grade must be an int, got {type(grade).__name__}")
    if not GRADE_MIN <= grade <= GRADE_MAX:
        raise ValidationError(
            f"Grade must be in [{GRADE_MIN}, {GRADE_MAX}], got {grade}"
        )

    student = find_by_id(students, student_id)
    if student is None:
        raise StudentNotFoundError(f"No student with id={student_id}")
    if grade not in student.grades:
        raise ValidationError(f"Student id={student_id} has no grade {grade}")

    remaining = list(student.grades)
    remaining.remove(grade)
    return update_grades(students, student_id, remaining)


def sort_students(students: Iterable[Student], key: SortKey) -> List[Student]:
    """Return a new sorted list.

    key:
        "avg"  - descending by average, then name a..z (stable tiebreak)
        "name" - ascending by name a..z
        "id"   - ascending by id
    """
    items = list(students)
    if key == "avg":
        return sorted(items, key=lambda s: (-s.average, s.name))
    if key == "name":
        return sorted(items, key=lambda s: s.name)
    if key == "id":
        return sorted(items, key=lambda s: s.id)
    raise ValidationError(f"Unknown sort key: {key!r}")


def filter_by_grade_range(
    students: Iterable[Student], min_avg: float, max_avg: float
) -> List[Student]:
    """Return students whose average is within [min_avg, max_avg]."""
    if min_avg > max_avg:
        raise ValidationError("min_avg must be <= max_avg")
    return [s for s in students if min_avg <= s.average <= max_avg]


def group_stats(students: List[Student]) -> dict:
    """Group statistics.

    Returns a dict:
        count       - number of students
        overall_avg - average over all grades of all students (0.0 if empty)
        best        - Student with the highest average, or None
        worst       - Student with the lowest average, or None
    """
    if not students:
        return {"count": 0, "overall_avg": 0.0, "best": None, "worst": None}

    # all_grades = [g for s in students for g in s.grades]
    all_grades = [g for s in students for g in s.present_grades]
    overall = sum(all_grades) / len(all_grades) if all_grades else 0.0
    best = max(students, key=lambda s: s.average)
    worst = min(students, key=lambda s: s.average)
    return {
        "count": len(students),
        "overall_avg": overall,
        "best": best,
        "worst": worst,
    }


def top_n(students: Iterable[Student], n: int) -> List[Student]:
    """Return the top-n students by average (descending, name tiebreak)."""
    if n < 0:
        raise ValidationError("n must be >= 0")
    return sort_students(students, "avg")[:n]


def max_grades_count(students: Iterable[Student]) -> int:
    """Maximum grade-list length across students (>= 0)."""
    return max((len(s.grades) for s in students), default=0)