"""CSV reading and writing for the students manager."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List

from .errors import CsvFormatError, ValidationError
from .models import Student


def load_students(path: str | Path) -> List[Student]:
    """Load students from a CSV file.

    Supports files with and without a header row. The header is detected
    by checking whether the first row starts with ``id`` (case-insensitive).

    Columns: ``id``, ``name``, then zero or more ``gradeN`` columns.
    Empty grade cells are treated as missing grades.

    Raises:
        CsvFormatError: if the file is malformed or a row cannot be parsed.
    """
    path = Path(path)
    try:
        f = path.open("r", encoding="utf-8", newline="")
    except FileNotFoundError as e:
        raise CsvFormatError(f"File not found: {path}") from e
    except PermissionError as e:
        raise CsvFormatError(f"Permission denied: {path}") from e

    with f:
        reader = csv.reader(f)
        try:
            rows = list(reader)
        except csv.Error as e:
            raise CsvFormatError(f"CSV parse error: {e}") from e

    if not rows:
        return []

    # Header detection: does the first row look like "id,name,..."?
    first = [c.strip().lower() for c in rows[0]]
    has_header = bool(first) and first[0] == "id"
    data_rows = rows[1:] if has_header else rows

    students: List[Student] = []
    seen_ids: set[int] = set()

    # for i, row in enumerate(data_rows, start=1 + (1 if has_header else 0)):
    #     try:
    #         student = _parse_row(row)
    #     except CsvFormatError:
    #         raise
    #     except ValidationError as e:
    #         raise CsvFormatError(f"Row {i}: {e}") from e
    #     if student.id in seen_ids:
    #         raise CsvFormatError(f"Row {i}: duplicate id {student.id}")
    #     seen_ids.add(student.id)
    #     students.append(student)



    for i, row in enumerate(data_rows, start=1 + (1 if has_header else 0)):
        try:
            student = _parse_row(row)
        except (CsvFormatError, ValidationError) as e:
            raise CsvFormatError(f"Row {i}: {e}") from e
        if student.id in seen_ids:
            raise CsvFormatError(f"Row {i}: duplicate id {student.id}")
        seen_ids.add(student.id)
        students.append(student)

    return students


def _parse_row(row: list[str]) -> Student:
    """Parse one CSV row into a Student. Empty trailing cells are OK."""
    if len(row) < 2:
        raise CsvFormatError(f"Expected at least 2 columns, got {len(row)}")

    raw_id, raw_name = row[0].strip(), row[1].strip()

    # id
    try:
        sid = int(raw_id)
    except ValueError as e:
        raise CsvFormatError(f"Invalid id {raw_id!r}") from e

    # name
    if not raw_name:
        raise CsvFormatError("Empty name")

    # grades
    grades: list[int] = []
    for cell in row[2:]:
        cell = cell.strip()
        if not cell: 
            grades.append(None)
            continue
        try:
            g = int(cell)
        except ValueError as e:
            raise CsvFormatError(f"Invalid grade {cell!r}") from e
        grades.append(g)

    # Student's __post_init__ will validate ranges and types
    return Student(sid, raw_name, grades)

def save_students(path: str | Path, students: Iterable[Student]) -> None:
    """Write students to a CSV file with a header.

    Columns are aligned: every student gets the same number of grade
    columns, missing ones become empty cells. Always UTF-8, newline=''.

    Raises:
        CsvFormatError: on I/O problems.
    """
    path = Path(path)
    student_list = list(students)
    max_g = max((len(s.grades) for s in student_list), default=0)
    header = ["id", "name"] + [f"grade{i}" for i in range(1, max_g + 1)]

    try:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for s in student_list:
                writer.writerow(s.to_row(max_grades=max_g))
    except PermissionError as e:
        raise CsvFormatError(f"Permission denied: {path}") from e
    except OSError as e:
        raise CsvFormatError(f"Cannot write {path}: {e}") from e


def export_top(path: str | Path, students: Iterable[Student], n: int) -> None:
    """Write the top-n students by average.

    Columns: id, name, average, grades (space-separated in one cell).

    Raises:
        ValidationError: if n < 0.
        CsvFormatError: on I/O problems.
    """
    from .processing import top_n  # local import to avoid a cycle

    if n < 0:
        raise ValidationError("n must be >= 0")

    top = top_n(students, n)
    path = Path(path)

    try:
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "name", "average", "grades"])
            for s in top:
                writer.writerow([
                    str(s.id),
                    s.name,
                    f"{s.average:.2f}",
                    # " ".join(str(g) for g in s.grades),
                    " ".join("-" if g is None else str(g) for g in s.grades)
                ])
    except PermissionError as e:
        raise CsvFormatError(f"Permission denied: {path}") from e
    except OSError as e:
        raise CsvFormatError(f"Cannot write {path}: {e}") from e