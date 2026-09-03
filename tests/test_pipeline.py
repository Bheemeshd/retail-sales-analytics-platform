"""End-to-end controls for the generated retail analytics product."""

import csv
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from retail_analytics.analytics import run_analytics  # noqa: E402
from retail_analytics.etl import build_database  # noqa: E402
from retail_analytics.generate import generate_dataset  # noqa: E402


class RetailPipelineTests(unittest.TestCase):
    def test_generator_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            generate_dataset(7, 80, 250, Path(first))
            generate_dataset(7, 80, 250, Path(second))
            for name in ("customers.csv", "products.csv", "stores.csv", "campaigns.csv", "orders.csv", "order_lines.csv"):
                self.assertEqual((Path(first) / name).read_bytes(), (Path(second) / name).read_bytes())

    def test_database_constraints_and_grain(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp, tempfile.TemporaryDirectory() as db_tmp:
            raw_path = Path(raw_tmp)
            db_path = Path(db_tmp) / "test.db"
            counts = generate_dataset(11, 120, 400, raw_path)
            loaded = build_database(raw_path, db_path)
            self.assertEqual(counts, loaded)
            with sqlite3.connect(db_path) as connection:
                self.assertEqual(connection.execute("PRAGMA foreign_key_check").fetchall(), [])
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM v_order_totals").fetchone()[0], 400)
                duplicates = connection.execute(
                    "SELECT COUNT(*) FROM (SELECT order_id,line_number FROM order_lines GROUP BY 1,2 HAVING COUNT(*)>1)"
                ).fetchone()[0]
                self.assertEqual(duplicates, 0)

    def test_kpi_reconciliation(self) -> None:
        with tempfile.TemporaryDirectory() as raw_tmp, tempfile.TemporaryDirectory() as db_tmp, tempfile.TemporaryDirectory() as out_tmp:
            raw_path, db_path, out_path = Path(raw_tmp), Path(db_tmp) / "test.db", Path(out_tmp)
            generate_dataset(21, 150, 600, raw_path)
            build_database(raw_path, db_path)
            summary = run_analytics(db_path, out_path, out_path / "powerbi")
            with sqlite3.connect(db_path) as connection:
                revenue = connection.execute("SELECT ROUND(SUM(net_revenue),2) FROM v_sales_detail WHERE status='Completed'").fetchone()[0]
            with (out_path / "monthly_kpis.csv").open(newline="", encoding="utf-8") as handle:
                monthly_total = round(sum(float(row["revenue"]) for row in csv.DictReader(handle)), 2)
            self.assertAlmostEqual(summary["total_revenue"], revenue, places=2)
            self.assertAlmostEqual(monthly_total, revenue, places=2)
            self.assertTrue(0 < summary["gross_margin_pct"] < 1)

    def test_checked_in_artifacts_are_valid(self) -> None:
        summary = json.loads((ROOT / "data" / "processed" / "executive_summary.json").read_text(encoding="utf-8"))
        self.assertTrue(summary["synthetic_data"])
        self.assertGreater(summary["completed_orders"], 10_000)
        for name in ("dashboard_preview.svg", "monthly_revenue.svg", "category_revenue.svg", "channel_revenue.svg", "customer_segments.svg"):
            content = (ROOT / "assets" / name).read_text(encoding="utf-8")
            self.assertTrue(content.startswith("<svg"))
            self.assertIn("</svg>", content)

    def test_public_sample_is_referentially_consistent(self) -> None:
        sample = ROOT / "data" / "sample"

        def rows(name: str) -> list[dict[str, str]]:
            with (sample / name).open(newline="", encoding="utf-8") as handle:
                return list(csv.DictReader(handle))

        customers = {row["customer_id"] for row in rows("customers_sample.csv")}
        products = {row["product_id"] for row in rows("products_sample.csv")}
        stores = {row["store_id"] for row in rows("stores_sample.csv")}
        campaigns = {row["campaign_id"] for row in rows("campaigns_sample.csv")}
        orders = rows("orders_sample.csv")
        order_ids = {row["order_id"] for row in orders}
        self.assertTrue(all(row["customer_id"] in customers for row in orders))
        self.assertTrue(all(not row["store_id"] or row["store_id"] in stores for row in orders))
        self.assertTrue(all(not row["campaign_id"] or row["campaign_id"] in campaigns for row in orders))
        for row in rows("order_lines_sample.csv"):
            self.assertIn(row["order_id"], order_ids)
            self.assertIn(row["product_id"], products)


if __name__ == "__main__":
    unittest.main()
