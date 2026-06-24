-- Databricks Data Analyst Medi
-- Query Insights lab / 14 - Slow query finder (current user)
-- =========================================================
-- Useful beyond this lab. Identifies statements to open in Query Profile by
-- statement_id. shuffle_mb + spilled_local_bytes highlight shuffle-heavy queries.

/* QI_DEMO_SLOW_QUERY_FINDER */
SELECT
  start_time,
  statement_id,
  client_application,
  query_tags,
  execution_status,
  total_duration_ms,
  waiting_at_capacity_duration_ms,
  execution_duration_ms,
  read_rows,
  ROUND(read_bytes / 1024 / 1024, 2) AS read_mb,
  ROUND(shuffle_read_bytes / 1024 / 1024, 2) AS shuffle_mb,
  spilled_local_bytes,
  from_result_cache,
  LEFT(statement_text, 240) AS statement_preview
FROM system.query.history
WHERE start_time >= current_timestamp() - INTERVAL 24 HOURS
  AND executed_by = current_user()
  AND execution_status = 'FINISHED'
ORDER BY total_duration_ms DESC
LIMIT 20;
