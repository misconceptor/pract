"""Tests for lab.models.Student."""

from __future__ import annotations

import pytest

from lab.errors import ValidationError
from lab.models import GRADE_MAX, GRADE_MIN, Student


class TestConstruction:
    def test_basic(self) -> None:
        s = Student(1, "Alice", [80, 90])
        assert s.id == 1
        assert s.name == "Alice"
        assert s.grades == [80, 90]

    def test_name_is_stripped(self) -> None:
        s = Student(1, "  Alice  ", [])
        assert s.name == "Alice"

    def test_default_grades_empty(self) -> None:
        s = Student(1, "Alice")
        assert s.grades == []

    def test_none_grade_allowed(self) -> None:
        s = Student(1, "Alice", [80, None, 90])
        assert s.grades == [80, None, 90]

    def test_all_none_grades_allowed(self) -> None:
        s = Student(1, "Alice", [None, None])
        assert s.grades == [None, None]


class TestIdValidation:
    def test_bool_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(True, "Alice", [])

    def test_non_int_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student("1", "Alice", [])  # type: ignore[arg-type]

    def test_negative_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(-1, "Alice", [])

    def test_zero_ok(self) -> None:
        assert Student(0, "Alice", []).id == 0


class TestNameValidation:
    def test_empty_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(1, "", [])

    def test_whitespace_only_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(1, "   ", [])

    def test_non_str_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(1, 42, [])  # type: ignore[arg-type]

    def test_cyrillic_ok(self) -> None:
        assert Student(1, "Иванов Иван", []).name == "Иванов Иван"


class TestGradesValidation:
    def test_non_list_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(1, "Alice", (80, 90))  # type: ignore[arg-type]

    def test_bool_grade_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(1, "Alice", [True])

    def test_non_int_grade_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(1, "Alice", ["80"])  # type: ignore[list-item]

    def test_below_min_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(1, "Alice", [GRADE_MIN - 1])

    def test_above_max_rejected(self) -> None:
        with pytest.raises(ValidationError):
            Student(1, "Alice", [GRADE_MAX + 1])

    def test_boundary_values_ok(self) -> None:
        assert Student(1, "Alice", [GRADE_MIN, GRADE_MAX]).grades == [0, 100]

    def test_error_mentions_index(self) -> None:
        with pytest.raises(ValidationError, match=r"grade\[1\]"):
            Student(1, "Alice", [80, 999])


class TestAverage:
    def test_regular(self) -> None:
        assert Student(1, "Alice", [80, 90, 100]).average == pytest.approx(90.0)

    def test_empty_is_zero(self) -> None:
        assert Student(1, "Alice", []).average == 0.0

    def test_only_none_is_zero(self) -> None:
        assert Student(1, "Alice", [None, None]).average == 0.0

    def test_none_skipped(self) -> None:
        # [90, None, 80] -> avg over 90 and 80 = 85.0 (not 170/3)
        assert Student(1, "Alice", [90, None, 80]).average == pytest.approx(85.0)

    def test_all_present_uses_all(self) -> None:
        assert Student(1, "Alice", [50, 50]).average == pytest.approx(50.0)


class TestPresentGrades:
    def test_filters_none(self) -> None:
        s = Student(1, "Alice", [80, None, 90, None])
        assert s.present_grades == [80, 90]

    def test_empty_when_all_none(self) -> None:
        assert Student(1, "Alice", [None, None]).present_grades == []


class TestToRow:
    def test_pads_to_max(self) -> None:
        s = Student(1, "Alice", [80, 90])
        assert s.to_row(4) == ["1", "Alice", "80", "90", "", ""]

    def test_none_becomes_empty_cell(self) -> None:
        s = Student(1, "Alice", [80, None, 90])
        assert s.to_row(3) == ["1", "Alice", "80", "", "90"]

    def test_exact_length_ok(self) -> None:
        s = Student(1, "Alice", [80, 90, 100])
        assert s.to_row(3) == ["1", "Alice", "80", "90", "100"]

    def test_max_smaller_than_grades_raises(self) -> None:
        s = Student(1, "Alice", [80, 90])
        with pytest.raises(ValidationError):
            s.to_row(1)

    def test_zero_max_empty_grades(self) -> None:
        assert Student(1, "Alice", []).to_row(0) == ["1", "Alice"]