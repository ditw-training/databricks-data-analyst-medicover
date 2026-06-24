-- Day 1 SQL Editor demo: RetailHub source discovery
-- 05 - Parameterized status and channel query
-- ==================================================
-- Change p_status and p_channel in SQL Editor and rerun.
-- Use p_channel = All to avoid filtering by channel.

USE SCHEMA silver;

SELECT
  status,
  channel,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(order_total_amount), 2) AS order_total_amount
FROM sales_orders
WHERE status = :p_status
  AND (:p_channel = 'All' OR channel = :p_channel)
GROUP BY status, channel
ORDER BY orders DESC;
