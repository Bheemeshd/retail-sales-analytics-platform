# Databricks notebook source
"""Silver adapter: type, validate and join the line-level sales contract."""

# COMMAND ----------
from pyspark.sql import functions as F

bronze = "portfolio.retail_bronze"
silver = "portfolio.retail_silver"

orders = spark.table(f"{bronze}.orders").withColumn("order_date", F.to_date("order_date"))
lines = spark.table(f"{bronze}.order_lines")
products = spark.table(f"{bronze}.products")
customers = spark.table(f"{bronze}.customers")

sales = (
    orders.join(lines, "order_id").join(products, "product_id").join(customers, "customer_id")
    .withColumn("net_revenue", F.when(F.col("status") == "Completed", F.col("quantity") * F.col("unit_price") * (1 - F.col("discount_pct"))).otherwise(F.lit(0.0)))
    .withColumn("gross_profit", F.when(F.col("status") == "Completed", F.col("net_revenue") - F.col("quantity") * F.col("unit_cost")).otherwise(F.lit(0.0)))
)

assert sales.filter(F.col("product_id").isNull() | F.col("customer_id").isNull()).count() == 0
sales.write.mode("overwrite").format("delta").saveAsTable(f"{silver}.sales_detail")
