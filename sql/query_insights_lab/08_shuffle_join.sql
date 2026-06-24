-- Databricks Data Analyst Medi
-- Query Insights lab / 08 - Shuffle (sort-merge) join
-- ===================================================
-- Goal: SHOW SHUFFLE AND NETWORK BANDWIDTH in the Query Profile.
--
-- This joins the large line-grain fact (gold.fact_sales) to the dimensions and
-- FORCES a shuffle / sort-merge join by disabling auto-broadcast. Both sides of
-- the join are re-partitioned (shuffled) across the network on the join key, so
-- the Query Profile shows a large "Shuffle" exchange with high
-- shuffle_read_bytes / shuffle_write_bytes (network bandwidth used).
--
-- Run this, then run 09_broadcast_join.sql and compare in Query Profile:
--   - 08 (this file): big Shuffle stage, both tables move across the network.
--   - 09:             little/no shuffle, only the small dimensions are shipped.
--
-- Query Profile talking points:
--   - Open the statement -> Graph view -> find the "Shuffle" / "Exchange" nodes,
--   - Read "Bytes" / "Rows" on the shuffle edges = bandwidth between executors,
--   - Note the join node is "SortMergeJoin" (not "BroadcastHashJoin"),
--   - In system.query.history compare shuffle_read_bytes vs file 09.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '10_shuffle_join';

-- Force a shuffle join: never broadcast a side, regardless of size.
-- (If the warehouse blocks SET, the SHUFFLE_MERGE hint below still applies.)
SET spark.sql.autoBroadcastJoinThreshold = -1;

/* QI_DEMO_10_SHUFFLE_JOIN */
SELECT /*+ SHUFFLE_MERGE(c, p) */
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
