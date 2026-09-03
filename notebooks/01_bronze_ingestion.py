# Databricks notebook source
"""Bronze adapter: ingest the six CSV contracts without business transformation."""

# COMMAND ----------
from pyspark.sql import functions as F

source_path = "/Volumes/portfolio/retail/raw"
bronze_catalog = "portfolio.retail_bronze"
tables = ["customers", "products", "stores", "campaigns", "orders", "order_lines"]

for table in tables:
    frame = (
        spark.read.option("header", True).option("inferSchema", True)
        .csv(f"{source_path}/{table}.csv")
        .withColumn("_ingested_at", F.current_timestamp())
        .withColumn("_source_file", F.input_file_name())
    )
    frame.write.mode("overwrite").format("delta").saveAsTable(f"{bronze_catalog}.{table}")
