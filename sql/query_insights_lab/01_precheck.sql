-- Databricks Data Analyst Medi
-- Query Insights lab / 01 - Pre-check
-- ==================================
-- Confirm that the W2 serving objects exist and have data.
-- Expected observation:
--   - v_fact_sales_incremental is line-grain detail,
--   - fact_sales_dashboard_monthly is a smaller serving aggregate,
--   - kpi_monthly is a compact KPI table.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '00_precheck';

/* QI_DEMO_00_PRECHECK */
SELECT
  'gold.v_fact_sales_incremental' AS object_name,
  COUNT(*) AS rows,
  COUNT(DISTINCT line_id) AS distinct_grain_keys
FROM gold.v_fact_sales_incremental
UNION ALL
SELECT
  'gold.fact_sales_dashboard_monthly',
  COUNT(*),
  COUNT(DISTINCT concat_ws('|', year_month, customer_region, category, channel))
FROM gold.fact_sales_dashboard_monthly
UNION ALL
SELECT
  'gold.kpi_monthly',
  COUNT(*),
  COUNT(DISTINCT year_month)
FROM gold.kpi_monthly
ORDER BY object_name;
