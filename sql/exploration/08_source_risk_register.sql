-- Day 1 SQL Editor demo: RetailHub source discovery
-- 08 - Source risk register query
-- ==================================================
-- Expected observation: these are modeling risks to document before building Gold.

USE SCHEMA silver;

SELECT 'unknown_status' AS risk_name, COUNT(*) AS affected_rows
FROM sales_orders
WHERE status NOT IN ('Completed', 'Returned', 'Cancelled')
UNION ALL
SELECT 'future_dated_orders', COUNT(*)
FROM sales_orders
WHERE order_date > current_date()
UNION ALL
SELECT 'null_unit_price_lines', COUNT(*)
FROM order_lines
WHERE unit_price IS NULL
UNION ALL
SELECT 'orphan_customer_lines', COUNT(*)
FROM order_lines l
LEFT ANTI JOIN customers c ON l.customer_id = c.customer_id
UNION ALL
SELECT 'orphan_product_lines', COUNT(*)
FROM order_lines l
LEFT ANTI JOIN products p ON l.product_id = p.product_id
ORDER BY affected_rows DESC;
