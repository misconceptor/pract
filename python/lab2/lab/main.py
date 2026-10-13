"""Console entry point: python -m lab.main.

Reads a menu choice from stdin, calls functions from processing/io_utils,
prints results. All expected errors are caught and shown as friendly
messages; the program never crashes on bad input.
"""

from __future__ import annotations

from pathlib import Path

from .errors import LabError, ValidationError
from .io_utils import export_top, load_students, save_students
from .models import Student
from .processing import (
    add_student,
    find_by_id,
    find_by_name,
    group_stats,
    remove_grade,
    remove_student,
    sort_students,
    top_n,
    update_grade_at,
    update_grades,
)


GREEN = "\033[92m"
ORANGE = "\033[38;5;208m"
RED = "\033[91m"
RESET = "\033[0m"

MENU = f"""
[ {GREEN}Student Manager{RESET} ]
{ORANGE}1{RESET}  Load students from CSV
{ORANGE}2{RESET}  Save students to CSV
{ORANGE}3{RESET}  Show all students
{ORANGE}4{RESET}  Add a student (marks sep by ,)
{ORANGE}5{RESET}  Remove student by id
{ORANGE}6{RESET}  Update grades by id (sep by ,)
{ORANGE}7{RESET}  Show group statistics
{ORANGE}8{RESET}  Export TOP-N students
{ORANGE}9{RESET}  Sort and show (avg | name | id)
{ORANGE}10{RESET} Remove specific grade by id
{ORANGE}11{RESET} Find student by id or name
{ORANGE}12{RESET} Update grade at index (0-based, '-' to clear)
{ORANGE}0{RESET}  Exit
"""


def ask(prompt: str) -> str:
    """Read a line from stdin, strip whitespace."""
    return input(prompt).strip()


def ask_int(prompt: str) -> int:
    """Read an int from stdin; raise ValidationError on bad input."""
    raw = ask(prompt)
    try:
        return int(raw)
    except ValueError as e:
        raise ValidationError(f"Expected an integer, got {raw!r}") from e


# def ask_grades(prompt: str) -> list[int]:
#     """Read grades separated by spaces or commas; empty line -> []."""
#     raw = ask(prompt)
#     if not raw:
#         return []
#     normalized = raw.replace(",", " ").split()
#     grades: list[int] = []
#     for token in normalized:
#         try:
#             grades.append(int(token))
#         except ValueError as e:
#             raise ValidationError(f"Invalid grade {token!r}") from e
#     return grades


def ask_grades(prompt: str) -> list[int | None]:
    """Comma-separated grades; empty token -> None (missing)."""
    raw = ask(prompt)
    if not raw:
        return []
    grades: list[int | None] = []
    for token in raw.split(","):
        token = token.strip()
        if not token:
            grades.append(None)
            continue
        try:
            grades.append(int(token))
        except ValueError as e:
            raise ValidationError(f"Invalid grade {token!r}") from e
    return grades

def show_students(students: list[Student], show_header: bool = True) -> None:
    """Print a table of students with aligned columns."""
    if not students:
        print("(no students)")
        return

    max_g = max((len(s.grades) for s in students), default=0)

    cols: list[tuple[str, int, str]] = [
        ("id", 6, ">"),
        ("name", 30, "<"),
        ("avg", 6, ">"),
    ]
    for i in range(max_g):
        cols.append((f"g{i + 1}", 4, ">"))

    if show_header:
        header = "  ".join(
            f"{title:{align}{width}}" for title, width, align in cols
        )
        divider = "-" * len(header)
        print(f"{GREEN}{header}{RESET}")
        print(f"{GREEN}{divider}{RESET}")

    for s in students:
        row = [f"{s.id:>6}", f"{s.name:<30}", f"{s.average:>6.2f}"]
        for i in range(max_g):
            if i < len(s.grades) and s.grades[i] is not None:
                row.append(f"{s.grades[i]:>4}")
            else:
                row.append(f"{'-':>4}")
        print("  ".join(row))


def show_stats(students: list[Student]) -> None:
    """Print group statistics."""
    stats = group_stats(students)
    print(f"Students:       {stats['count']}")
    print(f"Overall avg:    {stats['overall_avg']:.2f}")
    if stats["best"] is not None:
        b = stats["best"]
        print(f"Best student:   {b.name} (id={b.id}, avg={b.average:.2f})")
    if stats["worst"] is not None:
        w = stats["worst"]
        print(f"Worst student:  {w.name} (id={w.id}, avg={w.average:.2f})")


def handle_choice(choice: str, students: list[Student]) -> bool:
    """Run the action for `choice`. Return False to exit the loop."""
    if choice == "0":
        print(f"{ORANGE}Bye.{RESET}")
        return False

    if choice == "1":
        path = ask("CSV path: ")
        loaded = load_students(path)
        students.clear()
        students.extend(loaded)
        print(f"Loaded {len(loaded)} students.")

    elif choice == "2":
        if not students:
            print("Nothing to save.")
            return True
        path = ask("Save to CSV path: ")
        save_students(path, students)
        print(f"Saved {len(students)} students to {path}.")

    elif choice == "3":
        show_students(students)

    elif choice == "4":
        sid = ask_int("id: ")
        name = ask("name: ")
        grades = ask_grades("grades (space-separated, empty for none): ")
        add_student(students, Student(sid, name, grades))
        print(f"Added student id={sid}.")

    elif choice == "5":
        sid = ask_int("id to remove: ")
        removed = remove_student(students, sid)
        print(f"Removed {removed.name} (id={removed.id}).")

    elif choice == "6":
        sid = ask_int("id: ")
        grades = ask_grades("new grades (space-separated, empty to clear): ")
        updated = update_grades(students, sid, grades)
        print(f"Updated grades for {updated.name}: {updated.grades}.")

    elif choice == "7":
        show_stats(students)

    elif choice == "8":
        if not students:
            print("Nothing to export.")
            return True
        n = ask_int("N: ")
        path = ask("Export to CSV path: ")
        export_top(path, students, n)
        print(f"Exported top {n} to {path}.")

    elif choice == "9":
        key = ask("Sort key (avg|name|id): ").lower()
        result = sort_students(students, key)
        show_students(result)

    elif choice == "10":
        sid = ask_int("id: ")
        grade = ask_int("grade to remove: ")
        updated = remove_grade(students, sid, grade)
        print(f"Removed grade {grade} from {updated.name}: {updated.grades}.")

    elif choice == "11":
        query = ask("id or name: ")
        if query.isdigit():
            s = find_by_id(students, int(query))
            if s is None:
                print(f"No student with id={query}.")
            else:
                show_students([s])
        else:
            found = find_by_name(students, query)
            if not found:
                print(f"No students matching {query!r}.")
            else:
                show_students(found)

    elif choice == "12":
        sid = ask_int("id: ")
        idx = ask_int("index (0-based): ")
        raw = ask("new value (or '-' to clear): ").strip()
        if raw in ("", "-"):
            value: int | None = None
        else:
            try:
                value = int(raw)
            except ValueError as e:
                raise ValidationError(f"Expected int or '-', got {raw!r}") from e
        updated = update_grade_at(students, sid, idx, value)
        print(f"Updated grade[{idx}] for {updated.name}: {updated.grades}.")
    else:
        print(f"{RED}Unknown option: {choice!r}{RESET}")

    return True


def main() -> None:
    """Run the interactive menu loop."""
    students: list[Student] = []
    while True:
        print(MENU)
        try:
            choice = ask("> ")
            if not handle_choice(choice, students):
                return
        except LabError as e:
            print(f"{RED}Error: {e}{RESET}")
        except (KeyboardInterrupt, EOFError):
            print(f"{ORANGE}\nBye.{RESET}")
            return


if __name__ == "__main__":
    main()