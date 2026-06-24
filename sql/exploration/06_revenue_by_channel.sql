-- Day 1 SQL Editor demo: RetailHub source discovery
-- 06 - Parameterized date-window revenue by channel
-- ==================================================
-- Change p_start_date and p_end_date in SQL Editor and rerun.

USE SCHEMA silver;

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
