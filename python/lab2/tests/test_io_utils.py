"""Tests for lab.io_utils."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from lab.errors import CsvFormatError
from lab.io_utils import export_top, load_students, save_students
from lab.models import Student



class TestLoadBasic:
    def test_with_header(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,grade1,grade2\n1,Alice,80,90\n", encoding="utf-8")
        students = load_students(p)
        assert len(students) == 1
        assert students[0].id == 1
        assert students[0].grades == [80, 90]

    def test_without_header(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("1,Alice,80,90\n2,Bob,70,60\n", encoding="utf-8")
        students = load_students(p)
        assert [s.id for s in students] == [1, 2]

    def test_header_case_insensitive(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("ID,NAME,grade1\n1,Alice,80\n", encoding="utf-8")
        assert len(load_students(p)) == 1

    def test_empty_file_returns_empty(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("", encoding="utf-8")
        assert load_students(p) == []

    def test_header_only(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name\n", encoding="utf-8")
        assert load_students(p) == []


class TestLoadEmptyCells:
    def test_empty_middle_becomes_none(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,g1,g2,g3\n1,Alice,80,,90\n", encoding="utf-8")
        s = load_students(p)[0]
        assert s.grades == [80, None, 90]

    def test_empty_trailing_becomes_none(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,g1,g2,g3\n1,Alice,80,90,\n", encoding="utf-8")
        s = load_students(p)[0]
        assert s.grades == [80, 90, None]

    def test_all_empty_becomes_none_list(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,g1,g2\n1,Alice,,\n", encoding="utf-8")
        assert load_students(p)[0].grades == [None, None]

    def test_positions_are_preserved(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,g1,g2,g3\n1,Alice,,90,\n", encoding="utf-8")
        assert load_students(p)[0].grades == [None, 90, None]

    def test_whitespace_cell_is_none(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,g1,g2\n1,Alice,  ,80\n", encoding="utf-8")
        assert load_students(p)[0].grades == [None, 80]


class TestLoadErrors:
    def test_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(CsvFormatError, match="not found"):
            load_students(tmp_path / "nope.csv")

    def test_too_few_columns(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name\n1\n", encoding="utf-8")
        with pytest.raises(CsvFormatError):
            load_students(p)

    def test_bad_id(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name\nxyz,Alice\n", encoding="utf-8")
        with pytest.raises(CsvFormatError, match="Invalid id"):
            load_students(p)

    def test_empty_name(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name\n1,\n", encoding="utf-8")
        with pytest.raises(CsvFormatError, match="Empty name"):
            load_students(p)

    def test_bad_grade(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,g1\n1,Alice,abc\n", encoding="utf-8")
        with pytest.raises(CsvFormatError, match="Invalid grade"):
            load_students(p)

    def test_grade_out_of_range(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,g1\n1,Alice,101\n", encoding="utf-8")
        with pytest.raises(CsvFormatError):
            load_students(p)

    def test_duplicate_id(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name\n1,Alice\n1,Bob\n", encoding="utf-8")
        with pytest.raises(CsvFormatError, match="duplicate"):
            load_students(p)

    def test_error_mentions_row_number(self, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name\n1,Alice\n2,Bob\n3,,\n", encoding="utf-8")
        with pytest.raises(CsvFormatError, match="Row 4"):
            load_students(p)



class TestSaveBasic:
    def test_writes_header(self, tmp_path: Path) -> None:
        p = tmp_path / "out.csv"
        save_students(p, [Student(1, "Alice", [80, 90])])
        text = p.read_text(encoding="utf-8")
        first_line = text.splitlines()[0]
        assert first_line == "id,name,grade1,grade2"

    def test_pads_shorter_grades(self, tmp_path: Path) -> None:
        p = tmp_path / "out.csv"
        save_students(p, [
            Student(1, "Alice", [80, 90, 100]),
            Student(2, "Bob", [50]),
        ])
        rows = list(csv.reader(p.open(encoding="utf-8", newline="")))
        assert rows[2] == ["2", "Bob", "50", "", ""]

    def test_none_written_as_empty(self, tmp_path: Path) -> None:
        p = tmp_path / "out.csv"
        save_students(p, [Student(1, "Alice", [80, None, 90])])
        rows = list(csv.reader(p.open(encoding="utf-8", newline="")))
        assert rows[1] == ["1", "Alice", "80", "", "90"]

    def test_empty_students_list(self, tmp_path: Path) -> None:
        p = tmp_path / "out.csv"
        save_students(p, [])
        assert p.read_text(encoding="utf-8").strip() == "id,name"


class TestSaveErrors:
    def test_permission_denied(self, tmp_path: Path) -> None:
        # directory as target -> cannot open for writing as file
        d = tmp_path / "dir"
        d.mkdir()
        with pytest.raises(CsvFormatError):
            save_students(d, [Student(1, "Alice", [])])



class TestRoundTrip:
    def test_simple(self, tmp_path: Path) -> None:
        original = [Student(1, "Alice", [80, 90]), Student(2, "Bob", [50, 60])]
        p = tmp_path / "rt.csv"
        save_students(p, original)
        loaded = load_students(p)
        assert [(s.id, s.name, s.grades) for s in loaded] == \
               [(s.id, s.name, s.grades) for s in original]

    def test_with_none_preserved(self, tmp_path: Path) -> None:
        original = [
            Student(1, "Alice", [80, None, 90]),
            Student(2, "Bob", [None, None, 100]),
        ]
        p = tmp_path / "rt.csv"
        save_students(p, original)
        loaded = load_students(p)
        assert loaded[0].grades == [80, None, 90]
        assert loaded[1].grades == [None, None, 100]

    def test_cyrillic_and_unicode(self, tmp_path: Path) -> None:
        original = [Student(1, "Иванов Иван", [80]), Student(2, "Müller", [90])]
        p = tmp_path / "rt.csv"
        save_students(p, original)
        loaded = load_students(p)
        assert loaded[0].name == "Иванов Иван"
        assert loaded[1].name == "Müller"



class TestExportTop:
    def test_columns_and_order(self, tmp_path: Path, sample_students) -> None:
        p = tmp_path / "top.csv"
        export_top(p, sample_students, 2)
        rows = list(csv.reader(p.open(encoding="utf-8", newline="")))
        assert rows[0] == ["id", "name", "average", "grades"]
        # Carol (95) then Alice (80)
        assert rows[1][0] == "3" and rows[1][1] == "Carol"
        assert rows[2][0] == "1" and rows[2][1] == "Alice"

    def test_grades_space_separated(self, tmp_path: Path) -> None:
        p = tmp_path / "top.csv"
        export_top(p, [Student(1, "Alice", [80, 90, 100])], 1)
        rows = list(csv.reader(p.open(encoding="utf-8", newline="")))
        assert rows[1][3] == "80 90 100"

    def test_none_rendered_as_dash(self, tmp_path: Path) -> None:
        p = tmp_path / "top.csv"
        export_top(p, [Student(1, "Alice", [80, None, 90])], 1)
        rows = list(csv.reader(p.open(encoding="utf-8", newline="")))
        assert rows[1][3] == "80 - 90"

    def test_average_two_decimals(self, tmp_path: Path) -> None:
        p = tmp_path / "top.csv"
        export_top(p, [Student(1, "Alice", [80, 85, 90])], 1)
        rows = list(csv.reader(p.open(encoding="utf-8", newline="")))
        assert rows[1][2] == "85.00"

    def test_negative_n_raises(self, tmp_path: Path, sample_students) -> None:
        from lab.errors import ValidationError
        with pytest.raises(ValidationError):
            export_top(tmp_path / "t.csv", sample_students, -1)

    def test_zero_n_writes_header_only(self, tmp_path: Path, sample_students) -> None:
        p = tmp_path / "top.csv"
        export_top(p, sample_students, 0)
        rows = list(csv.reader(p.open(encoding="utf-8", newline="")))
        assert len(rows) == 1
        assert rows[0] == ["id", "name", "average", "grades"]

    def test_n_greater_than_size(self, tmp_path: Path, sample_students) -> None:
        p = tmp_path / "top.csv"
        export_top(p, sample_students, 100)
        rows = list(csv.reader(p.open(encoding="utf-8", newline="")))
        assert len(rows) == 4  # header + 3 students