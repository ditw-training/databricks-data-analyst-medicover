-- Day 1 SQL Editor demo: RetailHub source discovery
-- 09 - Header-vs-lines reconciliation sample
-- ==================================================
-- Expected observation: this detects source-system total mismatches.

USE SCHEMA silver;

WITH line_totals AS (
  SELECT
    order_id,
    ROUND(SUM(line_revenue), 2) AS line_revenue_total
  FROM order_lines
  GROUP BY order_id
)
SELECT
  o.order_id,
  o.order_date,
  o.status,
  o.order_total_amount,
  l.line_revenue_total,
  ROUND(o.order_total_amount - l.line_revenue_total, 2) AS amount_diff
FROM sales_orders o
JOIN line_totals l ON o.order_id = l.order_id
WHERE ABS(ROUND(o.order_total_amount - l.line_revenue_total, 2)) > 0.01
ORDER BY ABS(ROUND(o.order_total_amount - l.line_revenue_total, 2)) DESC, o.order_id
LIMIT 20;
