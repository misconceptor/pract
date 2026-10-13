"""Domain model: Student."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .errors import ValidationError

GRADE_MIN = 0
GRADE_MAX = 100

# A grade slot may be empty. Positions are preserved
Grade = Optional[int]


@dataclass
class Student:
    """A student with an id, name, and positional list of grades.

    Each element of `grades` is either an int in [0, 100] or None
    (missing grade). Position in the list is meaningful and preserved
    through load/save round-trips.

    Validation runs automatically on construction via __post_init__.
    """

    id: int
    name: str
    grades: List[Grade] = field(default_factory=list)

    def __post_init__(self) -> None:
        if isinstance(self.id, bool) or not isinstance(self.id, int):
            raise ValidationError(f"id must be int, got {self.id!r}")
        if self.id < 0:
            raise ValidationError(f"id must be non-negative, got {self.id}")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValidationError("name must be a non-empty string")
        self.name = self.name.strip()
        if not isinstance(self.grades, list):
            raise ValidationError("grades must be a list")
        for i, g in enumerate(self.grades):
            if g is None:
                continue
            if isinstance(g, bool) or not isinstance(g, int):
                raise ValidationError(
                    f"grade[{i}] must be int or None, got {g!r}"
                )
            if not (GRADE_MIN <= g <= GRADE_MAX):
                raise ValidationError(
                    f"grade[{i}] must be in [{GRADE_MIN}, {GRADE_MAX}], got {g}"
                )

    @property
    def present_grades(self) -> list[int]:
        """Grades that are actually set (None entries dropped)."""
        return [g for g in self.grades if g is not None]

    @property
    def average(self) -> float:
        """Average over present grades only. No grades -> 0.0."""
        present = self.present_grades
        return sum(present) / len(present) if present else 0.0

    def to_row(self, max_grades: int) -> list[str]:
        """Serialize to a CSV row.

        Missing grades (None) become empty cells. The row is right-padded
        with empty cells up to `max_grades` so that all rows in a file
        share the same number of columns.
        """
        if max_grades < len(self.grades):
            raise ValidationError(
                f"max_grades={max_grades} is smaller than {len(self.grades)} grades"
            )
        cells = ["" if g is None else str(g) for g in self.grades]
        cells += [""] * (max_grades - len(self.grades))
        return [str(self.id), self.name, *cells]