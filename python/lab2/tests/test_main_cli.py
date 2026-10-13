"""Tests for the CLI entry point lab.main."""

from __future__ import annotations

import builtins
from pathlib import Path

import pytest

import lab.main as cli
from lab.models import Student


# ---------- helpers ----------

def feed(monkeypatch, answers: list[str]) -> None:
    it = iter(answers)
    monkeypatch.setattr(builtins, "input", lambda prompt="": next(it))


def run(monkeypatch, capsys, answers: list[str]) -> str:
    feed(monkeypatch, answers)
    cli.main()
    return capsys.readouterr().out


# ---------- ask / parse helpers ----------

class TestAskInt:
    def test_ok(self, monkeypatch) -> None:
        monkeypatch.setattr(builtins, "input", lambda _="": "42")
        assert cli.ask_int("x: ") == 42

    def test_bad_raises(self, monkeypatch) -> None:
        from lab.errors import ValidationError
        monkeypatch.setattr(builtins, "input", lambda _="": "abc")
        with pytest.raises(ValidationError):
            cli.ask_int("x: ")


class TestAskGrades:
    def test_comma_separated(self, monkeypatch) -> None:
        monkeypatch.setattr(builtins, "input", lambda _="": "80,90,100")
        assert cli.ask_grades("g: ") == [80, 90, 100]

    def test_empty_slot_is_none(self, monkeypatch) -> None:
        monkeypatch.setattr(builtins, "input", lambda _="": "80,,90")
        assert cli.ask_grades("g: ") == [80, None, 90]

    def test_trailing_empty_slot(self, monkeypatch) -> None:
        monkeypatch.setattr(builtins, "input", lambda _="": "80,90,")
        assert cli.ask_grades("g: ") == [80, 90, None]

    def test_empty_line_returns_empty(self, monkeypatch) -> None:
        monkeypatch.setattr(builtins, "input", lambda _="": "")
        assert cli.ask_grades("g: ") == []

    def test_bad_token_raises(self, monkeypatch) -> None:
        from lab.errors import ValidationError
        monkeypatch.setattr(builtins, "input", lambda _="": "80,abc")
        with pytest.raises(ValidationError):
            cli.ask_grades("g: ")


# ---------- handle_choice in isolation ----------

class TestHandleChoice:
    def test_exit_returns_false(self, capsys) -> None:
        assert cli.handle_choice("0", []) is False

    def test_unknown_returns_true(self, capsys) -> None:
        assert cli.handle_choice("99", []) is True
        assert "Unknown option" in capsys.readouterr().out

    def test_show_all(self, capsys, sample_students) -> None:
        cli.handle_choice("3", sample_students)
        out = capsys.readouterr().out
        assert "Alice" in out and "Carol" in out

    def test_none_shown_as_dash(self, capsys) -> None:
        cli.handle_choice("3", [Student(1, "Alice", [80, None, 90])])
        out = capsys.readouterr().out
        assert "-" in out  # empty slot marked


# ---------- end-to-end scenarios ----------

class TestCliScenarios:
    def test_exit(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, ["0"])
        assert "Bye" in out

    def test_add_then_show(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, [
            "4",       # add
            "1",       # id
            "Alice",   # name
            "80,90",   # grades
            "3",       # show
            "0",
        ])
        assert "Added student id=1" in out
        assert "Alice" in out

    def test_add_with_empty_slot(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, [
            "4", "1", "Alice", "80,,90", "3", "0",
        ])
        assert "Alice" in out
        # p.3 output should show a dash for the empty slot

    def test_remove_unknown_shows_error(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, ["5", "42", "0"])
        assert "Error" in out
        assert "No student with id=42" in out

    def test_update_grade_at(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, [
            "4", "1", "Alice", "80,90,100",   # add
            "12",                              # update grade at
            "1",                               # id
            "1",                               # index
            "99",                              # value
            "0",
        ])
        assert "Updated grade[1]" in out
        assert "[80, 99, 100]" in out

    def test_update_grade_at_clear(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, [
            "4", "1", "Alice", "80,90",        # add
            "12", "1", "0", "-",               # clear index 0
            "0",
        ])
        assert "None" in out

    def test_find_by_id_found(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, [
            "4", "1", "Alice", "80",           # add
            "11", "1",                         # find by id 1
            "0",
        ])
        assert "Alice" in out

    def test_find_by_id_not_found(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, ["11", "99999", "0"])
        assert "No student with id=99999" in out

    def test_find_by_name(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, [
            "4", "1", "Alice", "80",
            "4", "2", "Bob", "70",
            "11", "alice",                     # substring, case-insensitive
            "0",
        ])
        assert "Alice" in out

    def test_bad_menu_int_does_not_crash(self, monkeypatch, capsys) -> None:
        out = run(monkeypatch, capsys, ["abc", "0"])
        # "abc" lands in else -> "Unknown option"; loop continues
        assert "Unknown option" in out
        assert "Bye" in out

    def test_eof_exits_gracefully(self, monkeypatch, capsys) -> None:
        def raise_eof(_=""):
            raise EOFError
        monkeypatch.setattr(builtins, "input", raise_eof)
        cli.main()
        assert "Bye" in capsys.readouterr().out

    def test_keyboard_interrupt_exits(self, monkeypatch, capsys) -> None:
        def raise_ki(_=""):
            raise KeyboardInterrupt
        monkeypatch.setattr(builtins, "input", raise_ki)
        cli.main()
        assert "Bye" in capsys.readouterr().out


# ---------- load/save via CLI ----------

class TestCliFileOps:
    def test_load_and_show(self, monkeypatch, capsys, tmp_path: Path) -> None:
        p = tmp_path / "s.csv"
        p.write_text("id,name,g1,g2\n1,Alice,80,90\n", encoding="utf-8")
        out = run(monkeypatch, capsys, [
            "1", str(p),   # load
            "3",           # show
            "0",
        ])
        assert "Loaded 1 students" in out
        assert "Alice" in out

    def test_save_round_trip(self, monkeypatch, capsys, tmp_path: Path) -> None:
        out_path = tmp_path / "out.csv"
        run(monkeypatch, capsys, [
            "4", "1", "Alice", "80,,90",     # add with empty slot
            "2", str(out_path),              # save
            "0",
        ])
        text = out_path.read_text(encoding="utf-8")
        assert "Alice" in text
        # empty slot preserved as empty cell
        assert "80,,90" in text or "80, ,90" in text