-- Every query should return zero rows or the expected reconciliation value.
SELECT order_id FROM order_lines GROUP BY order_id, line_number HAVING COUNT(*) > 1;
SELECT o.order_id FROM orders o LEFT JOIN customers c USING (customer_id) WHERE c.customer_id IS NULL;
SELECT ol.order_id FROM order_lines ol LEFT JOIN products p USING (product_id) WHERE p.product_id IS NULL;
SELECT order_id FROM orders WHERE (channel = 'Store') <> (store_id IS NOT NULL);
SELECT ROUND(SUM(net_revenue), 2) AS view_revenue FROM v_sales_detail WHERE status = 'Completed';
