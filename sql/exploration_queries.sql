-- Day 1 SQL Editor demo: RetailHub source discovery
-- ===================================================
--
-- Purpose:
--   Use this file in Databricks SQL Editor to demonstrate how analysts
--   explore governed Silver tables before any Gold modeling starts.
--
-- How to run in SQL Editor:
--   1. Open Databricks SQL Editor.
--   2. Create a new query and paste this file.
--   3. Replace YOUR_CATALOG with your participant catalog
--      (example: retailhub_jan_kowalski).
--   4. Select a SQL Warehouse.
--   5. Create the query parameters listed below.
--   6. Run one section at a time.
--
-- Query parameters to create in SQL Editor:
--   p_status      Text    Completed
--   p_start_date  Date    2024-01-01
--   p_end_date    Date    2024-12-31
--   p_channel     Text    All
--   p_top_n       Number  10
--
-- Parameter syntax:
--   Databricks SQL named parameters use :parameter_name.
--   Examples:
--     WHERE status = :p_status
--     WHERE order_date BETWEEN CAST(:p_start_date AS DATE)
--                          AND CAST(:p_end_date AS DATE)
--
-- Training rule:
--   SQL Editor is for fast exploration and saved analyst queries.
--   Repeatable course checks are reproduced in the notebook with %sql cells.

USE CATALOG YOUR_CATALOG;
USE SCHEMA silver;

-- 01. Confirm current SQL context.
-- Expected observation: catalog = your participant catalog, schema = silver.
SELECT
  current_user() AS current_user,
  current_catalog() AS catalog_name,
  current_schema() AS schema_name;

-- 02. Row counts across Silver tables.
-- Expected observation: customers/products are master data; orders/lines are transactional.
SELECT 'customers' AS table_name, COUNT(*) AS rows FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sales_orders', COUNT(*) FROM sales_orders
UNION ALL
SELECT 'order_lines', COUNT(*) FROM order_lines
ORDER BY table_name;

-- 03. Order header grain and date range.
-- Expected observation: rows should match distinct_orders for an order header table.
SELECT
  MIN(order_date) AS min_order_date,
  MAX(order_date) AS max_order_date,
  COUNT(*) AS rows,
  COUNT(DISTINCT order_id) AS distinct_orders,
  COUNT(*) - COUNT(DISTINCT order_id) AS duplicate_order_ids
FROM sales_orders;

-- 04. Order line grain.
-- Expected observation: line_rows is larger than distinct_orders.
SELECT
  COUNT(*) AS line_rows,
  COUNT(DISTINCT line_id) AS distinct_lines,
  COUNT(*) - COUNT(DISTINCT line_id) AS duplicate_line_ids,
  COUNT(DISTINCT order_id) AS distinct_orders,
  ROUND(COUNT(*) / COUNT(DISTINCT order_id), 2) AS avg_lines_per_order
FROM order_lines;

-- 05. Status distribution.
-- Expected observation: not every status should count as completed revenue.
SELECT
  status,
  COUNT(*) AS orders
FROM sales_orders
GROUP BY status
ORDER BY orders DESC;

-- 06. Parameterized status and channel query.
-- Change p_status and p_channel in SQL Editor and rerun.
-- Use p_channel = All to avoid filtering by channel.
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

-- 07. Parameterized date-window revenue by channel.
-- Change p_start_date and p_end_date in SQL Editor and rerun.
SELECT
  channel,
  COUNT(DISTINCT order_id) AS orders,
  ROUND(SUM(line_revenue), 2) AS revenue,
  ROUND(SUM(line_margin), 2) AS gross_margin,
  ROUND(100.0 * SUM(line_margin) / NULLIF(SUM(line_revenue), 0), 2) AS margin_rate_pct
FROM order_lines
WHERE status = :p_status
  AND order_date BETWEEN CAST(:p_start_date AS DATE) AND CAST(:p_end_date AS DATE)
  AND (:p_channel = 'All' OR channel = :p_channel)
GROUP BY channel
ORDER BY revenue DESC;

-- 08. Top-N products by revenue.
-- Change p_top_n in SQL Editor and rerun.
WITH product_revenue AS (
  SELECT
    product_id,
    category,
    ROUND(SUM(line_revenue), 2) AS revenue
  FROM order_lines
  WHERE status = :p_status
    AND order_date BETWEEN CAST(:p_start_date AS DATE) AND CAST(:p_end_date AS DATE)
    AND (:p_channel = 'All' OR channel = :p_channel)
  GROUP BY product_id, category
),
ranked AS (
  SELECT
    product_id,
    category,
    revenue,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
  FROM product_revenue
)
SELECT
  revenue_rank,
  product_id,
  category,
  revenue
FROM ranked
WHERE revenue_rank <= CAST(:p_top_n AS INT)
ORDER BY revenue_rank, product_id;

-- 09. Source risk register query.
-- Expected observation: these are modeling risks to document before building Gold.
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

-- 10. Header-vs-lines reconciliation sample.
-- Expected observation: this detects source-system total mismatches.
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
