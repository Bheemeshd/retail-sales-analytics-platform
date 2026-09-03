# Power BI implementation guide

No proprietary `.pbix` binary is required to review this repository. The pipeline writes versionable CSV extracts to `powerbi/extracts/`, all sourced from the same tested semantic layer used by SQL and Streamlit.

## Load

1. Import `fact_sales.csv` and `dim_customer.csv`.
2. Import the processed KPI files from `data/processed/` for reconciliation.
3. Create a calendar table from the minimum and maximum `order_date`.
4. Relate Calendar `[Date]` → Fact Sales `[order_date]` and Customer `[customer_id]` → Fact Sales `[customer_id]`.
5. Mark Calendar as the date table and hide technical keys from report view.

## Suggested pages

- Executive overview: revenue, profit, margin, AOV and YoY trend.
- Product performance: category/SKU scale, margin and discount analysis.
- Channel and stores: channel mix and region-normalized store leaderboard.
- Customers: RFM segment size, value and activation hypotheses.
- Campaigns: spend versus attributed revenue with a causality disclaimer.

See `model.md` for measures and the relationship diagram.
