-- Day 1 SQL Editor demo: RetailHub source discovery
-- 04 - Status distribution
-- ==================================================
-- Expected observation: not every status should count as completed revenue.

USE SCHEMA silver;

SELECT
  status,
  COUNT(*) AS orders
FROM sales_orders
GROUP BY status
ORDER BY orders DESC;
