-- Databricks Data Analyst Medi
-- Query Insights lab / 07 - EXPLAIN the serving aggregate
-- ======================================================
-- Same logical question as 06, but against the pre-aggregated serving table.
-- Compare the plan: fewer input files, smaller scan, lighter exchange.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '06_explain_aggregate';

/* QI_DEMO_06_EXPLAIN_AGGREGATE */
EXPLAIN FORMATTED
SELECT
  category,
  ROUND(SUM(revenue), 2) AS revenue
FROM gold.fact_sales_dashboard_monthly
WHERE order_month >= DATE '2024-01-01'
  AND order_month <  DATE '2025-01-01'
GROUP BY category
ORDER BY revenue DESC;
