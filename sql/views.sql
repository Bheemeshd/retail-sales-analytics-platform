CREATE VIEW v_sales_detail AS
SELECT
    o.order_id,
    o.order_date,
    substr(o.order_date, 1, 7) AS order_month,
    o.customer_id,
    c.region AS customer_region,
    c.acquisition_channel,
    c.loyalty_tier,
    o.channel,
    o.store_id,
    s.city AS store_city,
    s.store_format,
    o.campaign_id,
    ca.campaign_name,
    ca.marketing_channel,
    o.status,
    ol.line_number,
    ol.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    ol.quantity,
    ol.unit_price,
    ol.unit_cost,
    ol.discount_pct,
    CASE WHEN o.status = 'Completed'
         THEN ROUND(ol.quantity * ol.unit_price * (1 - ol.discount_pct), 2) ELSE 0 END AS net_revenue,
    CASE WHEN o.status = 'Completed'
         THEN ROUND(ol.quantity * (ol.unit_price * (1 - ol.discount_pct) - ol.unit_cost), 2) ELSE 0 END AS gross_profit
FROM orders o
JOIN order_lines ol ON ol.order_id = o.order_id
JOIN customers c ON c.customer_id = o.customer_id
JOIN products p ON p.product_id = ol.product_id
LEFT JOIN stores s ON s.store_id = o.store_id
LEFT JOIN campaigns ca ON ca.campaign_id = o.campaign_id;

CREATE VIEW v_order_totals AS
SELECT
    order_id,
    order_date,
    order_month,
    customer_id,
    customer_region,
    channel,
    store_id,
    campaign_id,
    status,
    ROUND(SUM(net_revenue), 2) AS net_revenue,
    ROUND(SUM(gross_profit), 2) AS gross_profit,
    SUM(quantity) AS units
FROM v_sales_detail
GROUP BY order_id, order_date, order_month, customer_id, customer_region,
         channel, store_id, campaign_id, status;
