-- Databricks Data Analyst Medi
-- Query Insights lab / 04 - Anti-pattern: function on date column
-- ==============================================================
-- Intentionally less BI-friendly: DATE_FORMAT on the filter column prevents
-- clean partition/file pruning, and the work runs against line-grain detail.
-- Use it to compare what should change before touching warehouse size.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '03_antipattern_date_function';

/* QI_DEMO_03_ANTIPATTERN_DATE_FUNCTION */
SELECT
  DATE_FORMAT(order_datetime, 'yyyy-MM') AS year_month,
  customer_region,
  category,
  COUNT(DISTINCT order_id) AS orders,
  COUNT(DISTINCT customer_id) AS customers,
  ROUND(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 2) AS revenue,
  ROUND(SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END), 2) AS gross_margin,
  ROUND(
    100.0 * SUM(CASE WHEN is_completed THEN line_margin ELSE 0 END)
    / NULLIF(SUM(CASE WHEN is_completed THEN line_revenue ELSE 0 END), 0),
    2
  ) AS margin_rate_pct
FROM gold.v_fact_sales_incremental
WHERE DATE_FORMAT(order_datetime, 'yyyy') = '2024'
  AND (:p_region = 'All' OR customer_region = :p_region)
  AND (:p_category = 'All' OR category = :p_category)
GROUP BY DATE_FORMAT(order_datetime, 'yyyy-MM'), customer_region, category
ORDER BY year_month, revenue DESC;
