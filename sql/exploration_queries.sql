-- Databricks SQL Editor exploration queries
-- Change YOUR_CATALOG to your assigned catalog name (e.g., retailhub_jan_kowalski)

USE CATALOG YOUR_CATALOG;
USE SCHEMA silver;

-- Step 1: Row counts across all Silver tables
SELECT 'customers'   AS tbl, COUNT(*) AS rows FROM customers
UNION ALL
SELECT 'products',          COUNT(*)          FROM products
UNION ALL
SELECT 'sales_orders',      COUNT(*)          FROM sales_orders
UNION ALL
SELECT 'order_lines',       COUNT(*)          FROM order_lines;

-- Step 2: Order date range and grain check
SELECT
  MIN(order_date)             AS min_date,
  MAX(order_date)             AS max_date,
  COUNT(*)                    AS total_orders,
  COUNT(DISTINCT order_id)    AS distinct_orders
FROM sales_orders;

-- Step 3: Status distribution
SELECT status, COUNT(*) AS cnt
FROM sales_orders
GROUP BY status
ORDER BY cnt DESC;

-- Step 4: Order lines grain
SELECT
  COUNT(*)                                      AS total_lines,
  COUNT(DISTINCT order_id)                      AS distinct_orders,
  ROUND(COUNT(*) / COUNT(DISTINCT order_id), 2) AS avg_lines_per_order
FROM order_lines;
