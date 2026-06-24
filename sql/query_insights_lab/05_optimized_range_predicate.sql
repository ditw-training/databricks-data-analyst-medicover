-- Databricks Data Analyst Medi
-- Query Insights lab / 05 - Optimized range predicate
-- ===================================================
-- The better equivalent of the 04 anti-pattern: a sargable range predicate on
-- the raw column plus the report-ready serving grain. Compare the Query Profile
-- scan/pruning stats against 04.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '04_optimized_range_predicate';

/* QI_DEMO_04_OPTIMIZED_RANGE_PREDICATE */
SELECT
  year_month,
  customer_region,
  category,
  SUM(completed_orders) AS orders,
  ROUND(SUM(revenue), 2) AS revenue,
  ROUND(SUM(gross_margin), 2) AS gross_margin,
  ROUND(100.0 * SUM(gross_margin) / NULLIF(SUM(revenue), 0), 2) AS margin_rate_pct
FROM gold.fact_sales_dashboard_monthly
WHERE order_month >= DATE '2024-01-01'
  AND order_month <  DATE '2025-01-01'
  AND (:p_region = 'All' OR customer_region = :p_region)
  AND (:p_category = 'All' OR category = :p_category)
GROUP BY year_month, customer_region, category
ORDER BY year_month, revenue DESC;
