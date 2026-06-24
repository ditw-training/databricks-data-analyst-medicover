-- Day 1 SQL Editor demo: RetailHub source discovery
-- 02 - Order header grain and date range
-- ==================================================
-- Expected observation: rows should match distinct_orders for an order header table.

USE SCHEMA silver;

SELECT
  MIN(order_date) AS min_order_date,
  MAX(order_date) AS max_order_date,
  COUNT(*) AS rows,
  COUNT(DISTINCT order_id) AS distinct_orders,
  COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_order_ids
FROM sales_orders;
