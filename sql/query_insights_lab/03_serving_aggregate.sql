-- Databricks Data Analyst Medi
-- Query Insights lab / 03 - Serving aggregate (optimized)
-- ======================================================
-- Pre-aggregated monthly serving table: the optimized equivalent of 02.
-- Query Profile talking points:
--   - fewer input rows,
--   - no line-grain COUNT(DISTINCT),
--   - simpler aggregation over a report-ready grain,
--   - this is the pattern expected by Import-friendly Power BI summary pages.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '02_serving_aggregate';

/* QI_DEMO_02_SERVING_AGGREGATE */
WITH aggregated AS (
  SELECT
    customer_region,
    category,
    channel,
    SUM(line_rows) AS line_rows,
    SUM(completed_orders) AS orders,
    ROUND(SUM(revenue), 2) AS revenue,
    ROUND(SUM(gross_margin), 2) AS gross_margin,
    ROUND(100.0 * SUM(gross_margin) / NULLIF(SUM(revenue), 0), 2) AS margin_rate_pct,
    ROUND(SUM(quantity), 2) AS quantity
  FROM gold.fact_sales_dashboard_monthly
  WHERE order_month >= CAST(:p_start_dt AS DATE)
    AND order_month <  CAST(:p_end_dt AS DATE)
    AND (:p_region = 'All' OR customer_region = :p_region)
    AND (:p_category = 'All' OR category = :p_category)
  GROUP BY customer_region, category, channel
),
ranked AS (
  SELECT
    *,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
  FROM aggregated
)
SELECT
  revenue_rank,
  customer_region,
  category,
  channel,
  line_rows,
  orders,
  revenue,
  gross_margin,
  margin_rate_pct,
  quantity
FROM ranked
WHERE revenue_rank <= CAST(:p_top_n AS INT)
ORDER BY revenue_rank, customer_region, category, channel;
