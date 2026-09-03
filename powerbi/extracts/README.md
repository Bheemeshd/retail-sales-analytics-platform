# Generated Power BI extracts

Run `python3 scripts/run_pipeline.py` to create:

- `fact_sales.csv`: governed line-level sales fact.
- `dim_customer.csv`: customer dimension with analytical segment.

The generated extracts are intentionally ignored by Git because they can be reproduced from the public-safe source generator. The Power BI model and DAX definitions remain version controlled in the parent folder.
