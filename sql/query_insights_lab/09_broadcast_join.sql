-- Databricks Data Analyst Medi
-- Query Insights lab / 09 - Broadcast join (low shuffle / bandwidth)
-- =================================================================
-- Same logical query as 08, but the small dimensions are BROADCAST to every
-- executor instead of shuffling the large fact. The big fact table stays put,
-- so the Query Profile shows little or no shuffle on the join: lower network
-- bandwidth and usually a faster wall-clock time.
--
-- Compare in Query Profile against 08_shuffle_join.sql:
--   - Join node is now "BroadcastHashJoin" + a "BroadcastExchange" on the dims,
--   - shuffle_read_bytes / shuffle_write_bytes are much smaller,
--   - only dim_customer + dim_product cross the network (broadcast once),
--   - the line-grain fact_sales is NOT re-partitioned.
--
-- Teaching point: broadcast wins when one side is small enough to fit in memory.
-- If you broadcast something too large you get memory pressure / spill instead,
-- so broadcast is a tool, not a default.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '11_broadcast_join';

-- Restore auto-broadcast (10 MB default) so small dims can be broadcast again.
-- The explicit BROADCAST hint below also forces it regardless of the threshold.
SET spark.sql.autoBroadcastJoinThreshold = 10485760;

/* QI_DEMO_11_BROADCAST_JOIN */
SELECT /*+ BROADCAST(c, p) */
  c.customer_region,
  c.segment,
  p.category,
  f.channel,
  COUNT(*) AS line_rows,
  COUNT(DISTINCT f.order_id) AS orders,
  ROUND(SUM(f.line_revenue), 2) AS revenue,
  ROUND(SUM(f.line_margin), 2) AS gross_margin,
  ROUND(100.0 * SUM(f.line_margin) / NULLIF(SUM(f.line_revenue), 0), 2) AS margin_rate_pct
FROM gold.fact_sales f
JOIN gold.dim_customer c
  ON f.customer_id = c.customer_id
JOIN gold.dim_product p
  ON f.product_id = p.product_id
WHERE f.order_date >= CAST(:p_start_dt AS DATE)
  AND f.order_date <  CAST(:p_end_dt AS DATE)
  AND f.is_completed
  AND (:p_region = 'All' OR c.customer_region = :p_region)
  AND (:p_category = 'All' OR p.category = :p_category)
GROUP BY c.customer_region, c.segment, p.category, f.channel
ORDER BY revenue DESC;
