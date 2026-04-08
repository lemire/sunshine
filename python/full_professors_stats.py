import argparse
import os
import sqlite3
import statistics
from typing import Iterable, List


EXCLUDED_TITLE_PATTERNS = [
    "assistant professor",
    "associate professor",
    "adjunct professor",
    "visiting professor",
    "emeritus professor",
    "professor emeritus",
]


def is_full_professor_title(job_title: str) -> bool:
    title = job_title.lower()
    if "professor" not in title:
        return False
    for excluded in EXCLUDED_TITLE_PATTERNS:
        if excluded in title:
            return False
    return True


def format_money(value: float) -> str:
    return f"${value:,.2f}"


def get_full_professor_salaries(db_path: str, universities_only: bool) -> List[float]:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = """
        SELECT s.salary, i.job_title, e.sector
        FROM salaries s
        JOIN individuals i ON s.individual_id = i.individual_id
        JOIN employers e ON s.employer_id = e.employer_id
    """

    params: Iterable[str] = []
    if universities_only:
        query += " WHERE e.sector = ?"
        params = ["Universities"]

    cursor.execute(query, tuple(params))
    rows = cursor.fetchall()
    conn.close()

    salaries: List[float] = []
    for row in rows:
        if is_full_professor_title(row["job_title"]):
            salaries.append(float(row["salary"]))

    return salaries


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute average and median salary for full professors in Ontario."
    )
    parser.add_argument(
        "db_file",
        nargs="?",
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "database.bin")),
        help="Path to SQLite database (default: ../database.bin).",
    )
    parser.add_argument(
        "--all-sectors",
        action="store_true",
        help="Do not restrict to the Universities sector.",
    )
    args = parser.parse_args()

    db_path = args.db_file
    if not os.path.exists(db_path):
        print(f"Error: Database not found: {db_path}")
        return

    salaries = get_full_professor_salaries(db_path, universities_only=not args.all_sectors)

    print(f"Source: {db_path}")
    print("Definition: job_title contains 'Professor' and excludes Assistant/Associate/Adjunct/Visiting/Emeritus ranks")
    print(f"Sector filter: {'Universities only' if not args.all_sectors else 'All sectors'}")

    if not salaries:
        print("No matching full professor records found.")
        return

    average_salary = statistics.mean(salaries)
    median_salary = statistics.median(salaries)

    print(f"Records matched: {len(salaries)}")
    print(f"Average salary: {format_money(average_salary)}")
    print(f"Median salary:  {format_money(median_salary)}")


if __name__ == "__main__":
    main()
