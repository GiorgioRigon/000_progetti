from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SCHEMA_PATH = BASE_DIR / "data" / "schema.sql"
DEFAULT_DB_PATH = BASE_DIR / "data" / "cis.sqlite3"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the local CIS SQLite database from the SQL schema."
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=DEFAULT_SCHEMA_PATH,
        help="Path to the SQL schema file.",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB_PATH,
        help="Path of the SQLite database file to create.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    schema_path = args.schema.resolve()
    db_path = args.db.resolve()

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    schema_sql = schema_path.read_text(encoding="utf-8")

    with sqlite3.connect(db_path) as connection:
        connection.executescript(schema_sql)
        connection.commit()

    print(f"Database initialized: {db_path}")


if __name__ == "__main__":
    main()
