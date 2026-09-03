-- 1. Monthly commercial performance and year-over-year revenue growth
WITH monthly AS (
    SELECT order_month,
           ROUND(SUM(net_revenue), 2) AS revenue,
           ROUND(SUM(gross_profit), 2) AS gross_profit,
           COUNT(DISTINCT order_id) AS orders,
           COUNT(DISTINCT customer_id) AS customers
    FROM v_sales_detail
    WHERE status = 'Completed'
    GROUP BY order_month
)
SELECT *,
       ROUND(100.0 * (revenue / LAG(revenue, 12) OVER (ORDER BY order_month) - 1), 2) AS yoy_revenue_pct
FROM monthly
ORDER BY order_month;

-- 2. Category performance: scale and margin quality
SELECT category,
       ROUND(SUM(net_revenue), 2) AS revenue,
       ROUND(SUM(gross_profit), 2) AS gross_profit,
       ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 2) AS margin_pct,
       SUM(quantity) AS units
FROM v_sales_detail
WHERE status = 'Completed'
GROUP BY category
ORDER BY revenue DESC;

-- 3. Channel economics and customer reach
SELECT channel,
       COUNT(DISTINCT order_id) AS orders,
       COUNT(DISTINCT customer_id) AS customers,
       ROUND(SUM(net_revenue), 2) AS revenue,
       ROUND(AVG(net_revenue), 2) AS revenue_per_line,
       ROUND(100.0 * SUM(gross_profit) / NULLIF(SUM(net_revenue), 0), 2) AS margin_pct
FROM v_sales_detail
WHERE status = 'Completed'
GROUP BY channel
ORDER BY revenue DESC;

-- 4. Store leaderboard with within-region rank
WITH store_kpis AS (
    SELECT customer_region AS region, store_id, store_city, store_format,
           ROUND(SUM(net_revenue), 2) AS revenue,
           ROUND(SUM(gross_profit), 2) AS gross_profit,
           COUNT(DISTINCT order_id) AS orders
    FROM v_sales_detail
    WHERE status = 'Completed' AND channel = 'Store'
    GROUP BY customer_region, store_id, store_city, store_format
)
SELECT *, RANK() OVER (PARTITION BY region ORDER BY revenue DESC) AS region_rank
FROM store_kpis
ORDER BY region, region_rank;

-- 5. Customer value and recency for activation design
SELECT customer_id,
       MAX(order_date) AS last_order_date,
       COUNT(DISTINCT order_id) AS completed_orders,
       ROUND(SUM(net_revenue), 2) AS lifetime_revenue,
       ROUND(SUM(gross_profit), 2) AS lifetime_gross_profit
FROM v_sales_detail
WHERE status = 'Completed'
GROUP BY customer_id
ORDER BY lifetime_revenue DESC;

-- 6. Attributed campaign performance (descriptive, not causal)
SELECT campaign_id, campaign_name, marketing_channel,
       COUNT(DISTINCT order_id) AS attributed_orders,
       ROUND(SUM(net_revenue), 2) AS attributed_revenue,
       ROUND(SUM(gross_profit), 2) AS attributed_gross_profit
FROM v_sales_detail
WHERE status = 'Completed' AND campaign_id IS NOT NULL
GROUP BY campaign_id, campaign_name, marketing_channel
ORDER BY attributed_revenue DESC;
