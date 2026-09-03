#!/usr/bin/env python3
"""Generate the public-safe source layer without running downstream steps."""

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retail_analytics.generate import generate_dataset  # noqa: E402


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--customers", type=int, default=3_000)
    parser.add_argument("--orders", type=int, default=18_000)
    args = parser.parse_args()
    print(json.dumps(generate_dataset(args.seed, args.customers, args.orders), indent=2))
