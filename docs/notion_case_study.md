# Retail Sales Analytics Platform

**Role simulated:** Retail / Commercial Data Analyst

**Tools:** SQL, Python, SQLite, Streamlit, Power BI modelling, Databricks/PySpark adapters, GitHub Actions

**Repository:** https://github.com/Bheemeshd/retail-sales-analytics-platform

> Portfolio disclosure: all customers, orders and euro values are deterministic synthetic data.

## Business problem

A multichannel retailer needs one governed view of revenue, margin, product, store, customer and campaign performance. The analytical product must help leadership decide where to protect margin, invest by channel, investigate store performance and design measured customer interventions.

## What I built

- Six synthetic source contracts covering customers, products, stores, campaigns, orders and order lines.
- A constrained SQLite model with canonical sales-detail and order-total views.
- Reusable SQL for YoY trends, category economics, channel contribution, store ranking, customer value and campaign attribution.
- Python orchestration that writes KPI marts, a Customer 360, RFM segments and Power BI extracts.
- An interactive Streamlit dashboard, a static HTML report and five GitHub-visible SVG visuals.
- Databricks/PySpark bronze, silver and gold deployment adapters.
- Automated determinism, integrity, reconciliation and artifact tests in GitHub Actions.

## Synthetic portfolio result

| Measure | Result |
| --- | ---: |
| Customers | 3,000 |
| Orders / order lines | 18,000 / 32,297 |
| Net revenue | €2.70m |
| Gross profit | €1.07m |
| Gross margin | 39.7% |
| Average order value | €162.90 |
| Return rate | 5.0% |
| Latest-month YoY revenue | −3.9% |

## Analytical judgment

The project separates scale from value: revenue is reviewed alongside gross profit, margin and discount depth. Store comparisons retain regional context. Campaign-linked orders are labeled attribution rather than incrementality because no counterfactual control group exists. RFM segments are framed as testable activation hypotheses, not permanent customer labels.

## Recommended decisions

1. Review high-revenue, low-margin SKUs before expanding discounts.
2. Investigate store outliers within region and format.
3. Use randomized campaign holdouts before making budget claims.
4. Test retention treatments on consented at-risk customers and measure incremental value.

## Limitations

The scenario is synthetic, product cost is simplified, and no production demand forecast is claimed. Real deployment would require approved source lineage, privacy controls, metric ownership and monitoring.
