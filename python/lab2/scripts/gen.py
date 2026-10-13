"""Generate a synthetic students.csv for the lab.

Usage:
    python scripts/generate_students.py
    python scripts/generate_students.py --rows 25 --max-grades 5 --out data/students.csv
    python scripts/generate_students.py --no-header --rows 10 --out data/students_no_header.csv
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

FIRST_NAMES = [
    # Male
    "James", "John", "Robert", "Michael", "William", "David", "Richard",
    "Joseph", "Thomas", "Charles", "Christopher", "Daniel", "Matthew",
    "Anthony", "Donald", "Mark", "Paul", "Steven", "Andrew", "Kenneth",
    "George", "Joshua", "Kevin", "Brian", "Edward", "Ronald", "Timothy",
    "Jason", "Jeffrey", "Ryan", "Jacob", "Gary", "Nicholas", "Eric",
    "Jonathan", "Stephen", "Larry", "Justin", "Scott", "Brandon",
    # Female
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara",
    "Susan", "Jessica", "Sarah", "Karen", "Nancy", "Lisa", "Betty",
    "Margaret", "Sandra", "Ashley", "Kimberly", "Emily", "Donna", "Michelle",
    "Carol", "Amanda", "Dorothy", "Melissa", "Deborah", "Stephanie",
    "Rebecca", "Sharon", "Laura", "Cynthia", "Kathleen", "Amy", "Angela",
    "Shirley", "Anna", "Brenda", "Pamela", "Emma", "Nicole", "Helen",
    # Neutral / international
    "Alex", "Sam", "Chris", "Jordan", "Taylor", "Casey", "Riley",
    "Morgan", "Jamie", "Avery",
]

LAST_NAMES = [
    # British / Irish / Scottish
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Miller", "Davis",
    "Wilson", "Anderson", "Taylor", "Moore", "Jackson", "Martin", "Thompson",
    "White", "Harris", "Clark", "Lewis", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Hill", "Green", "Baker", "Adams", "Nelson", "Carter",
    "Mitchell", "Roberts", "Turner", "Phillips", "Campbell", "Parker",
    "Evans", "Edwards", "Collins", "Stewart", "Morris", "Murphy", "Cook",
    "Rogers", "Morgan", "Bell", "Bailey", "Cooper", "Richardson", "Ward",
    "Cox", "Gray", "James", "Watson", "Brooks", "Kelly", "Sanders", "Price",
    "Bennett", "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins",
    "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores", "Washington",
    "Butler", "Simmons", "Foster", "Gonzales", "Bryant", "Alexander",
    "Russell", "Griffin", "Diaz", "Hayes",
    # Hispanic
    "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Perez", "Sanchez", "Ramirez", "Torres", "Flores", "Rivera", "Gomez",
    "Diaz", "Reyes", "Cruz", "Morales", "Ortiz", "Gutierrez", "Chavez",
    "Ramos", "Ruiz", "Alvarez", "Castillo", "Jimenez", "Vargas", "Mendoza",
    "Romero", "Herrera", "Medina", "Aguilar", "Vega", "Castro",
    # Italian
    "Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano",
    "Colombo", "Ricci", "Marino", "Greco", "Bruno", "Gallo", "Conti",
    "De Luca", "Costa", "Giordano", "Mancini", "Rizzo", "Lombardi",
    "Moretti", "Barbieri", "Fontana", "Santoro", "Mariani", "Rinaldi",
    # French
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit",
    "Durand", "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel",
    "Garcia", "David", "Bertrand", "Roux", "Vincent", "Fournier",
    # German / Austrian / Dutch
    "Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer",
    "Wagner", "Becker", "Schulz", "Hoffmann", "Schäfer", "Koch", "Bauer",
    "Richter", "Klein", "Wolf", "Schröder", "Neumann", "Schwarz",
    "Zimmermann", "Braun", "Krüger", "Hofmann", "Hartmann", "Lange",
    "de Vries", "Jansen", "van Dijk", "Bakker", "Visser",
    # Polish / Czech / Slavic
    "Nowak", "Kowalski", "Wiśniewski", "Wójcik", "Kowalczyk", "Kamiński",
    "Lewandowski", "Zieliński", "Szymański", "Woźniak", "Dąbrowski",
    "Kozłowski", "Jankowski", "Mazur", "Krawczyk", "Piotrowski",
    "Grabowski", "Nowicki", "Pawłowski", "Michalski", "Novák", "Svoboda",
    "Dvořák", "Černý", "Procházka", "Kučera", "Veselý", "Horák",
    # Scandinavian
    "Andersen", "Johansen", "Larsen", "Nielsen", "Hansen", "Pedersen",
    "Christensen", "Jensen", "Rasmussen", "Sørensen", "Kristensen",
    "Nilsson", "Eriksson", "Karlsson", "Larsson", "Olsson", "Persson",
    "Svensson", "Lindberg", "Berg", "Lund", "Holm", "Dahl",
    # Greek
    "Papadopoulos", "Papadakis", "Georgiou", "Dimitriou", "Nikolaou",
    "Christodoulou", "Vasileiou", "Petrou", "Karagiannis", "Antoniou",
    # Japanese / Korean / Chinese (romanized)
    "Sato", "Suzuki", "Takahashi", "Tanaka", "Watanabe", "Ito",
    "Yamamoto", "Nakamura", "Kobayashi", "Kato", "Yoshida", "Yamada",
    "Kim", "Lee", "Park", "Choi", "Jung", "Kang", "Cho", "Yoon",
    "Wang", "Li", "Zhang", "Liu", "Chen", "Yang", "Huang", "Zhao",
    "Wu", "Zhou", "Xu", "Sun", "Ma", "Zhu", "Hu", "Guo", "He",
    # Indian
    "Patel", "Sharma", "Singh", "Kumar", "Gupta", "Verma", "Reddy",
    "Rao", "Nair", "Menon", "Iyer", "Desai", "Shah", "Mehta", "Joshi",
    "Chowdhury", "Banerjee", "Mukherjee", "Kapoor", "Malhotra",
    # Arabic / Turkish / Persian
    "Al-Hassan", "Al-Ahmad", "Al-Sayed", "Al-Farsi", "Khalil", "Ibrahim",
    "Haddad", "Najjar", "Mansour", "Saleh", "Yılmaz", "Demir", "Kaya",
    "Çelik", "Şahin", "Yıldız", "Öztürk", "Ahmadi", "Hosseini",
    "Rezaei", "Karimi",
    # African / diaspora
    "Okafor", "Okonkwo", "Adeyemi", "Adebayo", "Mwangi", "Otieno",
    "Nkemdirim", "Diallo", "Traoré", "Cissé", "Mensah", "Boateng",
    "Ndlovu", "Dlamini", "Abebe", "Bekele", "Tesfaye",
]


def random_name(rng: random.Random) -> str:
    """Return a random 'First Last' name."""
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def random_grades(rng: random.Random, max_grades: int) -> list[int | None]:
    """Return a list of grades (0..100) with possible empty cells.

    Guarantees: length is `max_grades`, at least one grade is present,
    and the number of empty cells is at most max_grades // 2.
    """
    n = rng.randint(1, max_grades)
    n_empty = rng.randint(0, min(max_grades - n, max_grades // 2))
    grades: list[int | None] = [rng.randint(0, 100) for _ in range(n)]
    grades += [None] * n_empty
    rng.shuffle(grades)
    grades += [None] * (max_grades - len(grades))
    return grades


def generate(
    rows: int,
    max_grades: int,
    seed: int,
    with_header: bool,
) -> list[list[str]]:
    """Generate rows: [id, name, grade1, ..., gradeN] as strings."""
    rng = random.Random(seed)
    used_ids: set[int] = set()
    out: list[list[str]] = []

    if with_header:
        header = ["id", "name"] + [f"grade{i}" for i in range(1, max_grades + 1)]
        out.append(header)

    for _ in range(rows):
        # unique id in a reasonable range
        while True:
            sid = rng.randint(1, rows * 10)
            if sid not in used_ids:
                used_ids.add(sid)
                break
        name = random_name(rng)
        grades = random_grades(rng, max_grades)
        row = [str(sid), name] + ["" if g is None else str(g) for g in grades]
        out.append(row)

    return out


def write_csv(path: Path, rows: list[list[str]]) -> None:
    """Write rows to CSV with UTF-8 and newline=''."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate students.csv")
    parser.add_argument("--rows", type=int, default=15, help="number of students")
    parser.add_argument("--max-grades", type=int, default=4, help="max grade columns")
    parser.add_argument("--seed", type=int, default=42, help="random seed")
    parser.add_argument("--out", type=Path, default=Path("data/students.csv"))
    parser.add_argument("--no-header", action="store_true", help="omit header row")
    args = parser.parse_args()

    rows = generate(
        rows=args.rows,
        max_grades=args.max_grades,
        seed=args.seed,
        with_header=not args.no_header,
    )
    write_csv(args.out, rows)
    print(f"Written {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()