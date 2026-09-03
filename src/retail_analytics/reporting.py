"""Create portfolio-ready SVG visuals, HTML dashboard and executive memo."""

from __future__ import annotations

import csv
import html
import json
from pathlib import Path

from .config import ASSET_DIR, PROCESSED_DIR, REPORT_DIR, ensure_directories


INK = "#10243e"
MUTED = "#66788a"
BLUE = "#1f6feb"
TEAL = "#0e9f8a"
ORANGE = "#f59e0b"
BG = "#f4f7fb"
WHITE = "#ffffff"


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def _money(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"€{value / 1_000_000:.2f}m"
    if abs(value) >= 1_000:
        return f"€{value / 1_000:.1f}k"
    return f"€{value:,.0f}"


def _line_points(values: list[float], x: float, y: float, width: float, height: float) -> str:
    low, high = min(values), max(values)
    span = max(high - low, 1.0)
    return " ".join(
        f"{x + idx * width / max(len(values) - 1, 1):.1f},{y + height - (value - low) * height / span:.1f}"
        for idx, value in enumerate(values)
    )


def _write_chart(path: Path, title: str, labels: list[str], values: list[float], color: str, money: bool = True) -> None:
    width, height = 900, 470
    max_value = max(values) if values else 1.0
    bars = []
    for idx, (label, value) in enumerate(zip(labels, values)):
        bar_width = 640 * value / max_value
        y = 105 + idx * 62
        value_label = _money(value) if money else f"{value:,.0f}"
        bars.append(
            f'<text x="28" y="{y + 22}" font-size="15" fill="{INK}">{html.escape(label)}</text>'
            f'<rect x="210" y="{y}" width="{bar_width:.1f}" height="30" rx="6" fill="{color}" opacity="0.88"/>'
            f'<text x="{min(220 + bar_width, 820):.1f}" y="{y + 21}" font-size="14" fill="{INK}">{value_label}</text>'
        )
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<rect width="100%" height="100%" fill="{WHITE}"/><text x="28" y="46" font-size="25" font-weight="700" fill="{INK}">{html.escape(title)}</text>
<text x="28" y="72" font-size="13" fill="{MUTED}">Synthetic portfolio data · EUR</text>{''.join(bars)}</svg>'''
    path.write_text(svg, encoding="utf-8")


def build_reports(processed_dir: Path = PROCESSED_DIR, asset_dir: Path = ASSET_DIR) -> None:
    """Render all static artifacts from the curated KPI outputs."""
    ensure_directories()
    summary = json.loads((processed_dir / "executive_summary.json").read_text(encoding="utf-8"))
    monthly = _read_csv(processed_dir / "monthly_kpis.csv")
    categories = _read_csv(processed_dir / "category_performance.csv")
    channels = _read_csv(processed_dir / "channel_performance.csv")
    segments = _read_csv(processed_dir / "customer_segments.csv")

    _write_chart(asset_dir / "category_revenue.svg", "Revenue by category",
                 [r["category"] for r in categories], [float(r["revenue"]) for r in categories], BLUE)
    _write_chart(asset_dir / "channel_revenue.svg", "Revenue by sales channel",
                 [r["channel"] for r in channels], [float(r["revenue"]) for r in channels], TEAL)
    _write_chart(asset_dir / "customer_segments.svg", "Customer revenue by segment",
                 [r["segment"] for r in segments], [float(r["revenue"]) for r in segments], ORANGE)

    values = [float(row["revenue"]) for row in monthly]
    points = _line_points(values, 70, 100, 760, 270)
    ticks = "".join(
        f'<text x="{70 + i * 760 / max(len(values)-1,1):.1f}" y="405" text-anchor="middle" font-size="11" fill="{MUTED}">{row["order_month"]}</text>'
        for i, row in enumerate(monthly) if i % 3 == 0 or i == len(monthly) - 1
    )
    line_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="470" viewBox="0 0 900 470">
<rect width="100%" height="100%" fill="{WHITE}"/><text x="28" y="46" font-size="25" font-weight="700" fill="{INK}">Monthly net revenue</text>
<text x="28" y="72" font-size="13" fill="{MUTED}">24-month trend · synthetic portfolio data</text>
<line x1="70" y1="370" x2="830" y2="370" stroke="#d7e0ea"/><polyline points="{points}" fill="none" stroke="{BLUE}" stroke-width="4" stroke-linejoin="round"/>{ticks}</svg>'''
    (asset_dir / "monthly_revenue.svg").write_text(line_svg, encoding="utf-8")

    category_bars = []
    max_category = max(float(row["revenue"]) for row in categories)
    for idx, row in enumerate(categories):
        bar_height = 170 * float(row["revenue"]) / max_category
        x = 966 + idx * 82
        category_bars.append(
            f'<rect x="{x}" y="{708-bar_height:.1f}" width="54" height="{bar_height:.1f}" rx="7" fill="{TEAL}"/>'
            f'<text x="{x+27}" y="735" text-anchor="middle" font-size="10" fill="{MUTED}">{html.escape(row["category"][:7])}</text>'
        )
    dashboard = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="820" viewBox="0 0 1440 820">
<rect width="1440" height="820" fill="{BG}"/><rect x="0" y="0" width="1440" height="86" fill="{INK}"/>
<text x="48" y="44" font-size="28" font-weight="700" fill="white">Retail Sales Analytics Command Center</text>
<text x="48" y="68" font-size="13" fill="#b9c8d8">Executive view · 24 months · deterministic synthetic data</text>
<g font-family="Inter,Arial,sans-serif">
<rect x="42" y="116" width="318" height="116" rx="15" fill="{WHITE}"/><text x="66" y="151" font-size="14" fill="{MUTED}">NET REVENUE</text><text x="66" y="198" font-size="34" font-weight="700" fill="{INK}">{_money(summary['total_revenue'])}</text>
<rect x="382" y="116" width="318" height="116" rx="15" fill="{WHITE}"/><text x="406" y="151" font-size="14" fill="{MUTED}">GROSS PROFIT</text><text x="406" y="198" font-size="34" font-weight="700" fill="{INK}">{_money(summary['gross_profit'])}</text>
<rect x="722" y="116" width="318" height="116" rx="15" fill="{WHITE}"/><text x="746" y="151" font-size="14" fill="{MUTED}">GROSS MARGIN</text><text x="746" y="198" font-size="34" font-weight="700" fill="{INK}">{summary['gross_margin_pct']:.1%}</text>
<rect x="1062" y="116" width="336" height="116" rx="15" fill="{WHITE}"/><text x="1086" y="151" font-size="14" fill="{MUTED}">AVERAGE ORDER VALUE</text><text x="1086" y="198" font-size="34" font-weight="700" fill="{INK}">€{summary['average_order_value']:,.0f}</text>
<rect x="42" y="258" width="870" height="500" rx="15" fill="{WHITE}"/><text x="68" y="304" font-size="20" font-weight="700" fill="{INK}">Monthly revenue trend</text>
<line x1="95" y1="684" x2="870" y2="684" stroke="#d7e0ea"/><polyline points="{_line_points(values,95,350,775,334)}" fill="none" stroke="{BLUE}" stroke-width="5" stroke-linejoin="round"/>
<text x="95" y="720" font-size="13" fill="{MUTED}">{monthly[0]['order_month']}</text><text x="870" y="720" text-anchor="end" font-size="13" fill="{MUTED}">{monthly[-1]['order_month']}</text>
<rect x="934" y="258" width="464" height="232" rx="15" fill="{WHITE}"/><text x="960" y="302" font-size="20" font-weight="700" fill="{INK}">Decision signals</text>
<text x="960" y="347" font-size="14" fill="{MUTED}">Latest month YoY</text><text x="1328" y="347" text-anchor="end" font-size="21" font-weight="700" fill="{BLUE}">{summary['latest_month_yoy_pct']:.1%}</text>
<text x="960" y="391" font-size="14" fill="{MUTED}">Top category</text><text x="1328" y="391" text-anchor="end" font-size="18" font-weight="700" fill="{INK}">{html.escape(str(summary['top_category']))}</text>
<text x="960" y="435" font-size="14" fill="{MUTED}">Top channel</text><text x="1328" y="435" text-anchor="end" font-size="18" font-weight="700" fill="{INK}">{html.escape(str(summary['top_channel']))}</text>
<rect x="934" y="512" width="464" height="246" rx="15" fill="{WHITE}"/><text x="960" y="556" font-size="20" font-weight="700" fill="{INK}">Category scale</text>{''.join(category_bars)}
</g></svg>'''
    (asset_dir / "dashboard_preview.svg").write_text(dashboard, encoding="utf-8")

    table_rows = "".join(
        f"<tr><td>{html.escape(row['category'])}</td><td>{_money(float(row['revenue']))}</td><td>{float(row['margin_pct']):.1%}</td><td>{int(row['orders']):,}</td></tr>"
        for row in categories
    )
    html_report = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Retail Sales Executive Dashboard</title><style>body{{font-family:Inter,Arial,sans-serif;background:{BG};color:{INK};margin:0}}header{{background:{INK};color:white;padding:28px 6%}}main{{max-width:1180px;margin:auto;padding:28px}}.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}.card,.panel{{background:white;padding:22px;border-radius:14px;box-shadow:0 4px 18px #19324d12}}.value{{font-size:30px;font-weight:750;margin-top:8px}}.label{{color:{MUTED};font-size:13px}}.grid{{display:grid;grid-template-columns:2fr 1fr;gap:18px;margin-top:20px}}img{{width:100%}}table{{width:100%;border-collapse:collapse}}th,td{{padding:12px;text-align:left;border-bottom:1px solid #e7edf3}}th{{color:{MUTED};font-size:12px}}.note{{color:{MUTED};font-size:13px}}@media(max-width:850px){{.cards,.grid{{grid-template-columns:1fr 1fr}}}}</style></head>
<body><header><h1>Retail Sales Analytics Command Center</h1><p>Synthetic data · reproducible portfolio case study · EUR</p></header><main><div class="cards">
<div class="card"><div class="label">NET REVENUE</div><div class="value">{_money(summary['total_revenue'])}</div></div>
<div class="card"><div class="label">GROSS PROFIT</div><div class="value">{_money(summary['gross_profit'])}</div></div>
<div class="card"><div class="label">GROSS MARGIN</div><div class="value">{summary['gross_margin_pct']:.1%}</div></div>
<div class="card"><div class="label">AVERAGE ORDER VALUE</div><div class="value">€{summary['average_order_value']:,.0f}</div></div></div>
<div class="grid"><section class="panel"><img src="../assets/monthly_revenue.svg" alt="Monthly revenue trend"></section><aside class="panel"><h2>Executive signals</h2><p><b>{summary['latest_month_yoy_pct']:.1%}</b> latest-month YoY revenue</p><p><b>{html.escape(str(summary['top_category']))}</b> top category</p><p><b>{html.escape(str(summary['top_channel']))}</b> top channel</p><p><b>{summary['return_rate']:.1%}</b> order return rate</p></aside></div>
<section class="panel" style="margin-top:20px"><h2>Category performance</h2><table><thead><tr><th>Category</th><th>Revenue</th><th>Margin</th><th>Orders</th></tr></thead><tbody>{table_rows}</tbody></table></section>
<p class="note">All customers, orders and monetary values are synthetic. Campaign results are attributed associations, not causal lift estimates.</p></main></body></html>'''
    (REPORT_DIR / "executive_dashboard.html").write_text(html_report, encoding="utf-8")

    memo = f"""# Executive summary

## Portfolio snapshot

- **Net revenue:** {_money(summary['total_revenue'])}
- **Gross profit:** {_money(summary['gross_profit'])} ({summary['gross_margin_pct']:.1%} margin)
- **Completed orders:** {summary['completed_orders']:,} across {summary['active_customers']:,} active customers
- **Average order value:** €{summary['average_order_value']:,.2f}
- **Return rate:** {summary['return_rate']:.1%}

## Decision signals

- **{summary['top_category']}** is the largest category by revenue; commercial reviews should pair its scale with margin and discount depth.
- **{summary['top_channel']}** is the largest sales channel. Channel decisions should use both revenue and gross-profit contribution.
- Latest-month revenue is **{summary['latest_month_yoy_pct']:.1%} year over year** in this deterministic scenario.
- Customer segmentation identifies champions, loyal customers and an at-risk audience for controlled retention testing.

## Recommended actions

1. Review low-margin, high-revenue products before broad discounting.
2. Investigate store outliers within region rather than comparing raw totals alone.
3. Design randomized holdouts before interpreting campaign-attributed revenue as incremental impact.
4. Prioritize consented at-risk customers for a measured retention experiment.

## Scope boundary

All records and values are synthetic. The dashboard is a portfolio demonstration, not a production forecast or causal measurement system.
"""
    (REPORT_DIR / "executive_summary.md").write_text(memo, encoding="utf-8")
