-- Databricks notebook source
CREATE OR REPLACE TABLE portfolio.retail_gold.monthly_kpis AS
SELECT date_trunc('month', order_date) AS order_month,
       ROUND(SUM(net_revenue), 2) AS revenue,
       ROUND(SUM(gross_profit), 2) AS gross_profit,
       ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 4) AS margin_pct,
       COUNT(DISTINCT order_id) AS orders,
       COUNT(DISTINCT customer_id) AS customers,
       SUM(quantity) AS units
FROM portfolio.retail_silver.sales_detail
WHERE status = 'Completed'
GROUP BY date_trunc('month', order_date);

-- COMMAND ----------
CREATE OR REPLACE TABLE portfolio.retail_gold.category_performance AS
SELECT category,
       ROUND(SUM(net_revenue), 2) AS revenue,
       ROUND(SUM(gross_profit), 2) AS gross_profit,
       ROUND(SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 4) AS margin_pct,
       COUNT(DISTINCT order_id) AS orders
FROM portfolio.retail_silver.sales_detail
WHERE status = 'Completed'
GROUP BY category;
