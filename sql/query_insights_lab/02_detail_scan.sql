-- Databricks Data Analyst Medi
-- Query Insights lab / 02 - Detail scan (baseline / heavier)
-- =========================================================
-- Line-grain detail aggregation. This is the heavy baseline.
-- Query Profile talking points:
--   - scan: detail view reads more rows than the serving aggregate,
--   - filter: check whether the date range is applied early,
--   - aggregate: COUNT(DISTINCT) and GROUP BY require more work,
--   - output: LIMIT keeps returned rows small but does not remove upstream work.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '01_detail_scan';

/* QI_DEMO_01_DETAIL_SCAN */
WITH detail AS (
  SELECT
    customer_region,
    category,
    channel,
    order_id,
    line_id,
    line_revenue,
    line_margin,
    quantity
  FROM gold.v_fact_sales_incremental
  WHERE order_datetime >= CAST(:p_start_ts AS TIMESTAMP)
    AND order_datetime <  CAST(:p_end_ts AS TIMESTAMP)
    AND is_completed
    AND (:p_region = 'All' OR customer_region = :p_region)
    AND (:p_category = 'All' OR category = :p_category)
),
aggregated AS (
  SELECT
    customer_region,
    category,
    channel,
    COUNT(*) AS line_rows,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(line_revenue), 2) AS revenue,
    ROUND(SUM(line_margin), 2) AS gross_margin,
    ROUND(100.0 * SUM(line_margin) / NULLIF(SUM(line_revenue), 0), 2) AS margin_rate_pct,
    ROUND(SUM(quantity), 2) AS quantity
  FROM detail
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
