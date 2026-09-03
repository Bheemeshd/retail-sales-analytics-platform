# Databricks deployment adapters

These source-format notebooks show how the governed local data model maps to a medallion deployment. They are optional: the tested core pipeline runs locally with Python and SQLite.

Recommended execution order:

1. `01_bronze_ingestion.py`
2. `02_silver_sales.py`
3. `03_gold_kpis.sql`

Upload the files as Databricks source notebooks, set the source volume/catalog variables for your environment, and schedule them only after replacing the synthetic source contract with approved data.
