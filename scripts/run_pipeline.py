#!/usr/bin/env python3
"""Run the complete data-generation, ETL, analytics and reporting workflow."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retail_analytics.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--customers", type=int, default=3_000)
    parser.add_argument("--orders", type=int, default=18_000)
    args = parser.parse_args()
    result = run_pipeline(args.seed, args.customers, args.orders)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
