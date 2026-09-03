"""One-command orchestration for the retail analytics project."""

from __future__ import annotations

from .analytics import run_analytics
from .etl import build_database
from .generate import generate_dataset, write_public_sample
from .reporting import build_reports


def run_pipeline(seed: int = 42, customers: int = 3_000, orders: int = 18_000) -> dict:
    source_counts = generate_dataset(seed=seed, customers_count=customers, orders_count=orders)
    write_public_sample()
    database_counts = build_database()
    if source_counts != database_counts:
        raise ValueError(f"Source/database row-count mismatch: {source_counts} != {database_counts}")
    summary = run_analytics()
    build_reports()
    return {"source_counts": source_counts, "summary": summary}
