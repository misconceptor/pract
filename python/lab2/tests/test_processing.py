"""Tests for lab.processing."""

from __future__ import annotations

import pytest

from lab.errors import (
    DuplicateIdError,
    StudentNotFoundError,
    ValidationError,
)
from lab.models import Student
from lab.processing import (
    add_student,
    filter_by_grade_range,
    find_by_id,
    find_by_name,
    group_stats,
    max_grades_count,
    remove_grade,
    remove_student,
    sort_students,
    top_n,
    update_grade_at,
    update_grades,
)


# ---------- find_by_id ----------

class TestFindById:
    def test_found(self, sample_students) -> None:
        assert find_by_id(sample_students, 2) is sample_students[1]

    def test_not_found(self, sample_students) -> None:
        assert find_by_id(sample_students, 999) is None

    def test_empty(self) -> None:
        assert find_by_id([], 1) is None


# ---------- find_by_name ----------

class TestFindByName:
    def test_substring_case_insensitive(self) -> None:
        students = [Student(1, "Иванов Иван", []), Student(2, "Иванова Анна", [])]
        assert len(find_by_name(students, "иван")) == 2

    def test_no_match(self, sample_students) -> None:
        assert find_by_name(sample_students, "Zzz") == []

    def test_empty_query_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            find_by_name(sample_students, "   ")


# ---------- add_student ----------

class TestAddStudent:
    def test_adds(self, sample_students) -> None:
        s = Student(99, "Zed", [10])
        add_student(sample_students, s)
        assert sample_students[-1] is s

    def test_duplicate_raises(self, sample_students) -> None:
        with pytest.raises(DuplicateIdError):
            add_student(sample_students, Student(1, "Dup", []))


# ---------- remove_student ----------

class TestRemoveStudent:
    def test_removes_and_returns(self, sample_students) -> None:
        removed = remove_student(sample_students, 2)
        assert removed.id == 2
        assert find_by_id(sample_students, 2) is None

    def test_unknown_raises(self, sample_students) -> None:
        with pytest.raises(StudentNotFoundError):
            remove_student(sample_students, 999)


# ---------- update_grades ----------

class TestUpdateGrades:
    def test_replaces(self, sample_students) -> None:
        s = update_grades(sample_students, 1, [100, 100])
        assert s.grades == [100, 100]

    def test_unknown_raises(self, sample_students) -> None:
        with pytest.raises(StudentNotFoundError):
            update_grades(sample_students, 999, [1])

    def test_invalid_grades_do_not_mutate(self, sample_students) -> None:
        before = list(sample_students[0].grades)
        with pytest.raises(ValidationError):
            update_grades(sample_students, 1, [999])
        assert sample_students[0].grades == before

    def test_none_allowed(self, sample_students) -> None:
        s = update_grades(sample_students, 1, [80, None, 90])
        assert s.grades == [80, None, 90]


# ---------- update_grade_at ----------

class TestUpdateGradeAt:
    def test_replace_existing(self, sample_students) -> None:
        s = update_grade_at(sample_students, 1, 1, 100)
        assert s.grades == [90, 100, 70]

    def test_set_none(self, sample_students) -> None:
        s = update_grade_at(sample_students, 1, 0, None)
        assert s.grades[0] is None

    def test_extends_with_none(self, sample_students) -> None:
        s = update_grade_at(sample_students, 1, 5, 50)
        assert s.grades == [90, 80, 70, None, None, 50]

    def test_negative_index_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            update_grade_at(sample_students, 1, -1, 80)

    def test_unknown_id_raises(self, sample_students) -> None:
        with pytest.raises(StudentNotFoundError):
            update_grade_at(sample_students, 999, 0, 80)

    def test_invalid_value_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            update_grade_at(sample_students, 1, 0, 999)


# ---------- remove_grade ----------

class TestRemoveGrade:
    def test_removes_first_occurrence(self, sample_students) -> None:
        sample_students[0].grades = [80, 80, 90]
        s = remove_grade(sample_students, 1, 80)
        assert s.grades == [80, 90]

    def test_missing_value_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            remove_grade(sample_students, 1, 55)

    def test_unknown_id_raises(self, sample_students) -> None:
        with pytest.raises(StudentNotFoundError):
            remove_grade(sample_students, 999, 80)

    def test_out_of_range_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            remove_grade(sample_students, 1, 101)

    def test_bool_rejected(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            remove_grade(sample_students, 1, True)

    def test_none_value_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            remove_grade(sample_students, 1, None)  # type: ignore[arg-type]


# ---------- sort_students ----------

class TestSort:
    def test_by_avg_descending(self, sample_students) -> None:
        # Carol 95, Alice 80, Bob 50
        assert [s.id for s in sort_students(sample_students, "avg")] == [3, 1, 2]

    def test_by_avg_tiebreak_by_name(self) -> None:
        students = [
            Student(1, "Bob", [80]),
            Student(2, "Alice", [80]),
        ]
        assert [s.name for s in sort_students(students, "avg")] == ["Alice", "Bob"]

    def test_by_name(self, sample_students) -> None:
        assert [s.name for s in sort_students(sample_students, "name")] == \
               ["Alice", "Bob", "Carol"]

    def test_by_id(self, sample_students) -> None:
        assert [s.id for s in sort_students(sample_students, "id")] == [1, 2, 3]

    def test_unknown_key_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            sort_students(sample_students, "age")

    def test_returns_new_list(self, sample_students) -> None:
        result = sort_students(sample_students, "id")
        assert result is not sample_students

    def test_avg_uses_present_grades(self) -> None:
        # Carol [100, None, 90] -> avg 95, beats Alice [90,80,70] -> 80
        students = [Student(1, "Alice", [90, 80, 70]),
                    Student(2, "Carol", [100, None, 90])]
        assert [s.id for s in sort_students(students, "avg")] == [2, 1]


# ---------- filter_by_grade_range ----------

class TestFilter:
    def test_inclusive_bounds(self, sample_students) -> None:
        result = filter_by_grade_range(sample_students, 80, 95)
        assert sorted(s.id for s in result) == [1, 3]

    def test_empty_range(self, sample_students) -> None:
        assert filter_by_grade_range(sample_students, 200, 300) == []

    def test_min_greater_than_max_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            filter_by_grade_range(sample_students, 90, 10)


# ---------- group_stats ----------

class TestGroupStats:
    def test_empty(self) -> None:
        stats = group_stats([])
        assert stats == {"count": 0, "overall_avg": 0.0,
                         "best": None, "worst": None}

    def test_count(self, sample_students) -> None:
        assert group_stats(sample_students)["count"] == 3

    def test_overall_avg_over_all_grades(self, sample_students) -> None:
        # grades: 90+80+70 + 60+50+40 + 100+90 = 580 / 8 = 72.5
        assert group_stats(sample_students)["overall_avg"] == pytest.approx(72.5)

    def test_overall_avg_ignores_none(self) -> None:
        students = [Student(1, "A", [80, None, 100])]
        # avg over present: (80+100)/2 = 90, not /3
        assert group_stats(students)["overall_avg"] == pytest.approx(90.0)

    def test_overall_avg_zero_when_all_none(self) -> None:
        students = [Student(1, "A", [None, None])]
        assert group_stats(students)["overall_avg"] == 0.0

    def test_best_and_worst(self, sample_students) -> None:
        stats = group_stats(sample_students)
        assert stats["best"].id == 3   # Carol, avg 95
        assert stats["worst"].id == 2  # Bob, avg 50


# ---------- top_n ----------

class TestTopN:
    def test_returns_sorted_slice(self, sample_students) -> None:
        assert [s.id for s in top_n(sample_students, 2)] == [3, 1]

    def test_n_zero_returns_empty(self, sample_students) -> None:
        assert top_n(sample_students, 0) == []

    def test_n_greater_returns_all(self, sample_students) -> None:
        assert len(top_n(sample_students, 100)) == 3

    def test_negative_raises(self, sample_students) -> None:
        with pytest.raises(ValidationError):
            top_n(sample_students, -1)


# ---------- max_grades_count ----------

class TestMaxGradesCount:
    def test_empty(self) -> None:
        assert max_grades_count([]) == 0

    def test_max(self, sample_students) -> None:
        assert max_grades_count(sample_students) == 3

    def test_counts_none_slots(self) -> None:
        assert max_grades_count([Student(1, "A", [None, None, None])]) == 3