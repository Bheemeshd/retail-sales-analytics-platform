"""Reusable SQL-backed KPI and segmentation layer."""

from __future__ import annotations

import csv
import json
import sqlite3
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from .config import DATABASE_PATH, POWERBI_DIR, PROCESSED_DIR, ensure_directories


def _query(connection: sqlite3.Connection, sql: str) -> tuple[list[str], list[tuple]]:
    cursor = connection.execute(sql)
    return [item[0] for item in cursor.description], cursor.fetchall()


def _write_csv(path: Path, columns: list[str], rows: list[tuple] | list[list]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(columns)
        writer.writerows(rows)


def _month_offset(month: str, years: int = -1) -> str:
    year, month_number = month.split("-")
    return f"{int(year) + years:04d}-{month_number}"


def run_analytics(
    database_path: Path = DATABASE_PATH,
    output_dir: Path = PROCESSED_DIR,
    powerbi_dir: Path = POWERBI_DIR,
) -> dict[str, float | int | str]:
    """Calculate decision-focused retail KPIs and write reusable data marts."""
    ensure_directories()
    output_dir.mkdir(parents=True, exist_ok=True)
    powerbi_dir.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        monthly_columns, monthly_rows = _query(
            connection,
            """
            SELECT order_month,
                   ROUND(SUM(net_revenue), 2) AS revenue,
                   ROUND(SUM(gross_profit), 2) AS gross_profit,
                   COUNT(DISTINCT order_id) AS orders,
                   COUNT(DISTINCT customer_id) AS customers,
                   SUM(quantity) AS units
            FROM v_sales_detail
            WHERE status = 'Completed'
            GROUP BY order_month ORDER BY order_month
            """,
        )
        revenue_by_month = {row[0]: float(row[1]) for row in monthly_rows}
        monthly_enriched = []
        for month, revenue, profit, orders, customers, units in monthly_rows:
            prior = revenue_by_month.get(_month_offset(month))
            yoy = ((float(revenue) / prior) - 1.0) if prior else None
            monthly_enriched.append(
                [month, revenue, profit, round(float(profit) / float(revenue), 4), orders, customers,
                 units, round(float(revenue) / orders, 2), "" if yoy is None else round(yoy, 4)]
            )
        _write_csv(
            output_dir / "monthly_kpis.csv",
            monthly_columns[:3] + ["margin_pct", "orders", "customers", "units", "average_order_value", "yoy_revenue_pct"],
            monthly_enriched,
        )

        query_map = {
            "category_performance.csv": """
                SELECT category, ROUND(SUM(net_revenue),2) revenue, ROUND(SUM(gross_profit),2) gross_profit,
                       ROUND(SUM(gross_profit)/NULLIF(SUM(net_revenue),0),4) margin_pct,
                       COUNT(DISTINCT order_id) orders, SUM(quantity) units
                FROM v_sales_detail WHERE status='Completed'
                GROUP BY category ORDER BY revenue DESC""",
            "channel_performance.csv": """
                SELECT channel, ROUND(SUM(net_revenue),2) revenue, ROUND(SUM(gross_profit),2) gross_profit,
                       ROUND(SUM(gross_profit)/NULLIF(SUM(net_revenue),0),4) margin_pct,
                       COUNT(DISTINCT order_id) orders, COUNT(DISTINCT customer_id) customers
                FROM v_sales_detail WHERE status='Completed'
                GROUP BY channel ORDER BY revenue DESC""",
            "store_performance.csv": """
                SELECT store_id, store_city, customer_region region, store_format,
                       ROUND(SUM(net_revenue),2) revenue, ROUND(SUM(gross_profit),2) gross_profit,
                       COUNT(DISTINCT order_id) orders
                FROM v_sales_detail WHERE status='Completed' AND channel='Store'
                GROUP BY store_id, store_city, customer_region, store_format ORDER BY revenue DESC""",
            "product_performance.csv": """
                SELECT product_id, product_name, category, subcategory,
                       ROUND(SUM(net_revenue),2) revenue, ROUND(SUM(gross_profit),2) gross_profit,
                       SUM(quantity) units, COUNT(DISTINCT order_id) orders
                FROM v_sales_detail WHERE status='Completed'
                GROUP BY product_id, product_name, category, subcategory ORDER BY revenue DESC""",
            "campaign_performance.csv": """
                SELECT c.campaign_id, c.campaign_name, c.marketing_channel, c.spend,
                       COUNT(DISTINCT d.order_id) attributed_orders,
                       ROUND(COALESCE(SUM(d.net_revenue),0),2) attributed_revenue,
                       ROUND(COALESCE(SUM(d.gross_profit),0),2) attributed_gross_profit,
                       ROUND(COALESCE(SUM(d.net_revenue),0)/c.spend,2) attributed_roas
                FROM campaigns c LEFT JOIN v_sales_detail d
                  ON d.campaign_id=c.campaign_id AND d.status='Completed'
                GROUP BY c.campaign_id, c.campaign_name, c.marketing_channel, c.spend
                ORDER BY attributed_revenue DESC""",
        }
        for filename, sql in query_map.items():
            columns, rows = _query(connection, sql)
            _write_csv(output_dir / filename, columns, rows)

        customer_columns, customer_rows = _query(
            connection,
            """
            SELECT c.customer_id, c.region, c.acquisition_channel, c.loyalty_tier,
                   MAX(CASE WHEN d.status='Completed' THEN d.order_date END) last_order_date,
                   COUNT(DISTINCT CASE WHEN d.status='Completed' THEN d.order_id END) frequency,
                   ROUND(COALESCE(SUM(CASE WHEN d.status='Completed' THEN d.net_revenue ELSE 0 END),0),2) monetary,
                   ROUND(COALESCE(SUM(CASE WHEN d.status='Completed' THEN d.gross_profit ELSE 0 END),0),2) gross_profit
            FROM customers c LEFT JOIN v_sales_detail d ON d.customer_id=c.customer_id
            GROUP BY c.customer_id, c.region, c.acquisition_channel, c.loyalty_tier
            """,
        )
        reference_date = date.fromisoformat(connection.execute("SELECT MAX(order_date) FROM orders").fetchone()[0])
        customer_output = []
        segment_counts: Counter[str] = Counter()
        segment_revenue: defaultdict[str, float] = defaultdict(float)
        for customer_id, region, acquisition, loyalty, last_order, frequency, monetary, profit in customer_rows:
            recency = (reference_date - date.fromisoformat(last_order)).days if last_order else 999
            if frequency >= 8 and monetary >= 900 and recency <= 120:
                segment = "Champions"
            elif frequency >= 4 and recency <= 180:
                segment = "Loyal"
            elif recency <= 90:
                segment = "Recent"
            elif frequency >= 3 and recency > 240:
                segment = "At Risk"
            elif frequency == 0:
                segment = "No Purchase"
            else:
                segment = "Occasional"
            segment_counts[segment] += 1
            segment_revenue[segment] += float(monetary)
            customer_output.append([customer_id, region, acquisition, loyalty, last_order or "", recency,
                                    frequency, monetary, profit, segment])
        customer_360_columns = customer_columns[:5] + ["recency_days"] + customer_columns[5:] + ["segment"]
        _write_csv(output_dir / "customer_360.csv", customer_360_columns, customer_output)
        segment_rows = [
            [segment, segment_counts[segment], round(segment_revenue[segment], 2),
             round(segment_revenue[segment] / max(segment_counts[segment], 1), 2)]
            for segment in sorted(segment_counts, key=lambda item: segment_revenue[item], reverse=True)
        ]
        _write_csv(output_dir / "customer_segments.csv", ["segment", "customers", "revenue", "revenue_per_customer"], segment_rows)

        total_revenue, total_profit, completed_orders, active_customers, units = connection.execute(
            """SELECT ROUND(SUM(net_revenue),2), ROUND(SUM(gross_profit),2),
                      COUNT(DISTINCT order_id), COUNT(DISTINCT customer_id), SUM(quantity)
               FROM v_sales_detail WHERE status='Completed'"""
        ).fetchone()
        all_orders, returned_orders = connection.execute(
            "SELECT COUNT(*), SUM(status='Returned') FROM orders"
        ).fetchone()
        latest_month = monthly_enriched[-1]
        best_category = connection.execute(
            """SELECT category, ROUND(SUM(net_revenue),2) revenue FROM v_sales_detail
               WHERE status='Completed' GROUP BY category ORDER BY revenue DESC LIMIT 1"""
        ).fetchone()
        best_channel = connection.execute(
            """SELECT channel, ROUND(SUM(net_revenue),2) revenue FROM v_sales_detail
               WHERE status='Completed' GROUP BY channel ORDER BY revenue DESC LIMIT 1"""
        ).fetchone()
        summary: dict[str, float | int | str] = {
            "synthetic_data": True,
            "total_revenue": float(total_revenue),
            "gross_profit": float(total_profit),
            "gross_margin_pct": round(float(total_profit) / float(total_revenue), 4),
            "completed_orders": int(completed_orders),
            "active_customers": int(active_customers),
            "units_sold": int(units),
            "average_order_value": round(float(total_revenue) / int(completed_orders), 2),
            "return_rate": round(int(returned_orders) / int(all_orders), 4),
            "latest_month": str(latest_month[0]),
            "latest_month_revenue": float(latest_month[1]),
            "latest_month_yoy_pct": float(latest_month[-1]) if latest_month[-1] != "" else 0.0,
            "top_category": str(best_category[0]),
            "top_category_revenue": float(best_category[1]),
            "top_channel": str(best_channel[0]),
            "top_channel_revenue": float(best_channel[1]),
        }
        (output_dir / "executive_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

        # Flat, documented extracts make the same semantic layer easy to connect in Power BI.
        fact_columns, fact_rows = _query(
            connection,
            """SELECT order_id, order_date, order_month, customer_id, product_id, category, subcategory,
                      channel, store_id, campaign_id, status, quantity, discount_pct, net_revenue, gross_profit
               FROM v_sales_detail""",
        )
        _write_csv(powerbi_dir / "fact_sales.csv", fact_columns, fact_rows)
        _write_csv(powerbi_dir / "dim_customer.csv", customer_columns[:4] + ["segment"],
                   [[r[0], r[1], r[2], r[3], r[-1]] for r in customer_output])
    return summary
