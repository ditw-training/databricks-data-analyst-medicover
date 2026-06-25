-- Day 1 SQL Editor demo: RetailHub source discovery
-- 03 - Order line grain
-- ==================================================
-- Expected result: line_rows is larger than distinct_orders.

USE SCHEMA silver;

SELECT
  COUNT(*) AS line_rows,
  COUNT(DISTINCT line_id) AS distinct_lines,
  COUNT(*) - COUNT(DISTINCT line_id) AS duplicate_line_ids,
  COUNT(DISTINCT order_id) AS distinct_orders,
  ROUND(COUNT(*) / COUNT(DISTINCT order_id), 2) AS avg_lines_per_order
FROM order_lines;
