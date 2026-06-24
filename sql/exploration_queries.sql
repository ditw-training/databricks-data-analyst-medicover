-- Databricks Data Analyst Medicover
-- SQL Editor exploration queries
-- =================================
-- Use this file in SQL Editor for the Day 1 source-discovery demo.
-- Replace YOUR_CATALOG with the participant catalog or select the catalog
-- in the SQL Editor UI before running.
--
-- Suggested SQL Editor parameters:
--   p_status     = Completed
--   p_start_date = 2024-01-01
--   p_end_date   = 2024-12-31
--   p_channel    = All
--   p_top_n      = 10

USE CATALOG YOUR_CATALOG;
USE SCHEMA silver;

-- 1. Row counts across key source tables.
SELECT 'silver.sales_orders' AS object_name, COUNT(*) AS rows
FROM silver.sales_orders
UNION ALL
SELECT 'silver.order_lines', COUNT(*)
FROM silver.order_lines
UNION ALL
SELECT 'silver.customers', COUNT(*)
FROM silver.customers
UNION ALL
SELECT 'silver.products', COUNT(*)
FROM silver.products
ORDER BY object_name;

-- 2. Order header grain and date range.
SELECT
  COUNT(*) AS header_rows,
  COUNT(DISTINCT order_id) AS distinct_orders,
  MIN(order_date) AS min_order_date,
  MAX(order_date) AS max_order_date
FROM silver.sales_orders;

-- 3. Parameterized status/channel exploration.
SELECT
  status,
  channel,
  COUNT(DISTINCT order_id) AS orders
FROM silver.sales_orders
WHERE order_date >= CAST(:p_start_date AS DATE)
  AND order_date <= CAST(:p_end_date AS DATE)
  AND (:p_status = 'All' OR status = :p_status)
  AND (:p_channel = 'All' OR channel = :p_channel)
GROUP BY status, channel
ORDER BY orders DESC;

-- 4. Top products by completed revenue.
SELECT
  p.category,
  p.product_name,
  ROUND(SUM(ol.line_revenue), 2) AS revenue,
  COUNT(DISTINCT ol.order_id) AS orders
FROM silver.order_lines ol
JOIN silver.products p
  ON ol.product_id = p.product_id
WHERE ol.order_date >= CAST(:p_start_date AS DATE)
  AND ol.order_date <= CAST(:p_end_date AS DATE)
  AND ol.status = 'Completed'
GROUP BY p.category, p.product_name
ORDER BY revenue DESC
LIMIT CAST(:p_top_n AS INT);

-- 5. Header-vs-lines reconciliation sample.
SELECT
  h.order_id,
  h.status AS header_status,
  COUNT(l.line_id) AS line_rows,
  ROUND(SUM(l.line_revenue), 2) AS line_revenue
FROM silver.sales_orders h
LEFT JOIN silver.order_lines l
  ON h.order_id = l.order_id
WHERE h.order_date >= CAST(:p_start_date AS DATE)
  AND h.order_date <= CAST(:p_end_date AS DATE)
GROUP BY h.order_id, h.status
ORDER BY line_rows DESC, h.order_id
LIMIT 50;
