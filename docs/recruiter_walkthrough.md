# Five-minute recruiter walkthrough

1. Start with the dashboard image in the README: explain the commercial question and the four executive KPIs.
2. Open `sql/views.sql`: show the governed semantic definition of revenue and gross profit.
3. Open `src/retail_analytics/pipeline.py`: demonstrate the one-command source-to-report workflow.
4. Open `sql/analysis.sql`: discuss window functions, category economics, store ranking and customer value.
5. Open `app/streamlit_app.py`: show how the same marts support interactive decision exploration.
6. Close with `tests/`: explain deterministic data, referential integrity, reconciliation and artifact validation.

## Interview narrative

“I built this as a decision product rather than a chart collection. The pipeline starts with a documented synthetic source contract, enforces relational and commercial rules in SQLite, centralizes KPI definitions, then exposes the same governed outputs through SQL, Python, Streamlit, static reporting and Power BI-ready extracts. I also make the attribution-versus-causality boundary explicit so campaign metrics are not overclaimed.”
