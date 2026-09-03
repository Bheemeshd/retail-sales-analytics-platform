"""Load generated CSV sources into a constrained SQLite analytical layer."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path

from .config import DATABASE_PATH, RAW_DIR, ROOT, ensure_directories


TABLES = ("customers", "products", "stores", "campaigns", "orders", "order_lines")


def _rows(path: Path) -> tuple[list[str], list[tuple[str, ...]]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        return header, [tuple(value if value != "" else None for value in row) for row in reader]


def build_database(raw_dir: Path = RAW_DIR, database_path: Path = DATABASE_PATH) -> dict[str, int]:
    """Recreate and populate the SQLite database, returning loaded row counts."""
    ensure_directories()
    if database_path.exists():
        database_path.unlink()
    with sqlite3.connect(database_path) as connection:
        connection.executescript((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
        counts: dict[str, int] = {}
        for table in TABLES:
            header, rows = _rows(raw_dir / f"{table}.csv")
            placeholders = ", ".join("?" for _ in header)
            columns = ", ".join(header)
            connection.executemany(f"INSERT INTO {table} ({columns}) VALUES ({placeholders})", rows)
            counts[table] = len(rows)
        connection.executescript((ROOT / "sql" / "views.sql").read_text(encoding="utf-8"))
        connection.commit()
        violations = connection.execute("PRAGMA foreign_key_check").fetchall()
        if violations:
            raise ValueError(f"Foreign-key violations detected: {violations[:5]}")
    return counts
