-- Databricks Data Analyst Medi
-- Query Insights lab / 06 - EXPLAIN the detail scan
-- =================================================
-- Read the physical plan before running large variants in a shared SQL Warehouse session.
-- Look for: file scan on v_fact_sales_incremental, the pushed-down filter, and
-- the aggregate/exchange stages.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '05_explain_detail';

/* QI_DEMO_05_EXPLAIN_DETAIL */
EXPLAIN FORMATTED
SELECT
  category,
  ROUND(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 2) AS revenue
FROM gold.v_fact_sales_incremental
WHERE order_datetime >= TIMESTAMP '2024-01-01 00:00:00'
  AND order_datetime <  TIMESTAMP '2025-01-01 00:00:00'
GROUP BY category
ORDER BY revenue DESC;
