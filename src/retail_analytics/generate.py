"""Generate a deterministic, public-safe retail commerce dataset."""

from __future__ import annotations

import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

from .config import RAW_DIR, ROOT, ensure_directories


REGIONS = {
    "North": ["Lille", "Rouen", "Amiens"],
    "South": ["Marseille", "Toulouse", "Nice"],
    "East": ["Lyon", "Strasbourg", "Grenoble"],
    "West": ["Rennes", "Nantes", "Bordeaux"],
}
CATEGORIES = {
    "Electronics": ("Audio", "Computing", "Accessories", 110.0),
    "Home": ("Kitchen", "Decor", "Storage", 48.0),
    "Apparel": ("Menswear", "Womenswear", "Footwear", 42.0),
    "Beauty": ("Skincare", "Fragrance", "Wellness", 31.0),
    "Sports": ("Fitness", "Outdoor", "Team Sports", 55.0),
}
CHANNELS = ("Store", "Web", "Mobile App", "Marketplace")


def _write_csv(path: Path, rows: Iterable[dict], fieldnames: list[str]) -> int:
    materialized = list(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(materialized)
    return len(materialized)


def _random_date(rng: random.Random, start: date, end: date) -> date:
    return start + timedelta(days=rng.randrange((end - start).days + 1))


def generate_dataset(
    seed: int = 42,
    customers_count: int = 3_000,
    orders_count: int = 18_000,
    output_dir: Path = RAW_DIR,
) -> dict[str, int]:
    """Create customers, products, stores, campaigns, orders and order lines."""
    ensure_directories()
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    customers = []
    region_names = list(REGIONS)
    acquisition_channels = ["Organic", "Paid Search", "Paid Social", "Referral", "Email"]
    for idx in range(1, customers_count + 1):
        signup = _random_date(rng, date(2022, 1, 1), date(2025, 10, 31))
        customers.append(
            {
                "customer_id": f"C{idx:06d}",
                "signup_date": signup.isoformat(),
                "region": rng.choices(region_names, weights=[24, 25, 27, 24])[0],
                "acquisition_channel": rng.choices(acquisition_channels, weights=[32, 22, 16, 13, 17])[0],
                "loyalty_tier": rng.choices(["None", "Silver", "Gold", "Platinum"], weights=[48, 30, 17, 5])[0],
            }
        )

    products = []
    product_id = 1
    for category, (sub1, sub2, sub3, base_price) in CATEGORIES.items():
        for subcategory in (sub1, sub2, sub3):
            for number in range(1, 9):
                list_price = round(base_price * rng.uniform(0.55, 1.95), 2)
                unit_cost = round(list_price * rng.uniform(0.43, 0.72), 2)
                products.append(
                    {
                        "product_id": f"P{product_id:04d}",
                        "product_name": f"{subcategory} {number:02d}",
                        "category": category,
                        "subcategory": subcategory,
                        "list_price": f"{list_price:.2f}",
                        "unit_cost": f"{unit_cost:.2f}",
                    }
                )
                product_id += 1

    stores = []
    store_id = 1
    for region, cities in REGIONS.items():
        for city in cities:
            for store_format in ("High Street", "Retail Park"):
                stores.append(
                    {
                        "store_id": f"S{store_id:03d}",
                        "city": city,
                        "region": region,
                        "store_format": store_format,
                        "opened_date": _random_date(rng, date(2016, 1, 1), date(2022, 12, 31)).isoformat(),
                    }
                )
                store_id += 1

    campaigns = []
    campaign_channels = ["Email", "Paid Search", "Paid Social", "Affiliate"]
    for idx in range(1, 17):
        start = date(2024, 1, 8) + timedelta(days=(idx - 1) * 45)
        campaigns.append(
            {
                "campaign_id": f"CMP{idx:03d}",
                "campaign_name": f"{campaign_channels[(idx - 1) % 4]} Wave {(idx - 1) // 4 + 1}",
                "marketing_channel": campaign_channels[(idx - 1) % 4],
                "start_date": start.isoformat(),
                "end_date": (start + timedelta(days=27)).isoformat(),
                "spend": f"{rng.uniform(8000, 26000):.2f}",
            }
        )

    product_lookup = {row["product_id"]: row for row in products}
    store_by_region = {
        region: [row["store_id"] for row in stores if row["region"] == region]
        for region in region_names
    }
    campaign_windows = [
        (row["campaign_id"], date.fromisoformat(row["start_date"]), date.fromisoformat(row["end_date"]))
        for row in campaigns
    ]
    orders = []
    order_lines = []
    start_date, end_date = date(2024, 1, 1), date(2025, 12, 31)
    for idx in range(1, orders_count + 1):
        customer = rng.choice(customers)
        order_date = _random_date(rng, start_date, end_date)
        # Increase probability in November/December to create realistic seasonality.
        if rng.random() < 0.18:
            order_date = date(rng.choice([2024, 2025]), rng.choice([11, 12]), rng.randint(1, 28))
        channel = rng.choices(CHANNELS, weights=[42, 27, 22, 9])[0]
        store_id_value = rng.choice(store_by_region[customer["region"]]) if channel == "Store" else ""
        eligible_campaigns = [cid for cid, first, last in campaign_windows if first <= order_date <= last]
        campaign_id_value = rng.choice(eligible_campaigns) if eligible_campaigns and rng.random() < 0.36 else ""
        status = rng.choices(["Completed", "Returned", "Cancelled"], weights=[92, 5, 3])[0]
        payment_method = rng.choices(["Card", "Digital Wallet", "Gift Card", "Bank Transfer"], weights=[63, 23, 8, 6])[0]
        orders.append(
            {
                "order_id": f"O{idx:07d}",
                "customer_id": customer["customer_id"],
                "order_date": order_date.isoformat(),
                "channel": channel,
                "store_id": store_id_value,
                "campaign_id": campaign_id_value,
                "status": status,
                "payment_method": payment_method,
            }
        )
        line_count = rng.choices([1, 2, 3, 4], weights=[46, 34, 15, 5])[0]
        selected_products = rng.sample(products, line_count)
        for line_number, product in enumerate(selected_products, start=1):
            quantity = rng.choices([1, 2, 3], weights=[76, 19, 5])[0]
            loyalty_discount = {"None": 0.0, "Silver": 0.03, "Gold": 0.06, "Platinum": 0.09}[customer["loyalty_tier"]]
            campaign_discount = rng.choice([0.05, 0.10, 0.15]) if campaign_id_value else 0.0
            discount = min(0.30, loyalty_discount + campaign_discount + (0.05 if rng.random() < 0.10 else 0.0))
            price_noise = rng.uniform(0.97, 1.03)
            order_lines.append(
                {
                    "order_id": f"O{idx:07d}",
                    "line_number": line_number,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": f"{float(product['list_price']) * price_noise:.2f}",
                    "unit_cost": product_lookup[product["product_id"]]["unit_cost"],
                    "discount_pct": f"{discount:.4f}",
                }
            )

    counts = {
        "customers": _write_csv(output_dir / "customers.csv", customers, list(customers[0])),
        "products": _write_csv(output_dir / "products.csv", products, list(products[0])),
        "stores": _write_csv(output_dir / "stores.csv", stores, list(stores[0])),
        "campaigns": _write_csv(output_dir / "campaigns.csv", campaigns, list(campaigns[0])),
        "orders": _write_csv(output_dir / "orders.csv", orders, list(orders[0])),
        "order_lines": _write_csv(output_dir / "order_lines.csv", order_lines, list(order_lines[0])),
    }
    manifest = {
        "synthetic": True,
        "seed": seed,
        "date_range": [start_date.isoformat(), end_date.isoformat()],
        "counts": counts,
        "grain": {"orders": "one row per order", "order_lines": "one row per order-product line"},
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return counts


def write_public_sample(
    raw_dir: Path = RAW_DIR,
    sample_dir: Path = ROOT / "data" / "sample",
    transactional_rows: int = 250,
) -> None:
    """Write a compact, referentially consistent sample from the full sources."""
    sample_dir.mkdir(parents=True, exist_ok=True)

    def read_table(table: str) -> list[dict[str, str]]:
        with (raw_dir / f"{table}.csv").open(newline="", encoding="utf-8") as source:
            return list(csv.DictReader(source))

    orders = read_table("orders")[:transactional_rows]
    order_ids = {row["order_id"] for row in orders}
    order_lines = [row for row in read_table("order_lines") if row["order_id"] in order_ids]
    required = {
        "customers": {row["customer_id"] for row in orders},
        "products": {row["product_id"] for row in order_lines},
        "stores": {row["store_id"] for row in orders if row["store_id"]},
        "campaigns": {row["campaign_id"] for row in orders if row["campaign_id"]},
    }
    keys = {"customers": "customer_id", "products": "product_id", "stores": "store_id", "campaigns": "campaign_id"}
    selected: dict[str, list[dict[str, str]]] = {"orders": orders, "order_lines": order_lines}
    for table, key in keys.items():
        selected[table] = [row for row in read_table(table) if row[key] in required[table]]

    for table in ("customers", "products", "stores", "campaigns", "orders", "order_lines"):
        rows = selected[table]
        with (sample_dir / f"{table}_sample.csv").open("w", newline="", encoding="utf-8") as target:
            writer = csv.DictWriter(target, fieldnames=list(rows[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
