# Methodology and limitations

## Analytical workflow

1. Generate a deterministic two-year commerce scenario with realistic category, channel, seasonality and discount variation.
2. Validate relationships and business rules while loading the CSV contract into SQLite.
3. Build a canonical line-level view and order-level aggregate.
4. Calculate revenue, profit, margin, customer, store, product and campaign marts.
5. Render the same governed outputs into static GitHub visuals, an HTML report, Streamlit and Power BI extracts.

## Controls

- Primary, foreign-key and check constraints in SQLite.
- Source-to-database row-count reconciliation.
- Unique order-line grain.
- Store presence constrained to the store channel.
- Revenue reconciliation between the semantic view, monthly mart and executive summary.
- Determinism and artifact-validity tests in CI.

## Limitations

- Synthetic data demonstrates analytical method, not real commercial performance.
- Product cost is modeled as a stable standard cost and excludes logistics, returns processing and overhead.
- Campaign linkage is attribution, not causal incrementality. It cannot establish what would have happened without exposure.
- RFM thresholds are transparent heuristics; production segmentation requires calibration and outcome testing.
- Forecasting is intentionally out of scope because the scenario does not contain real demand shocks or operational constraints.
