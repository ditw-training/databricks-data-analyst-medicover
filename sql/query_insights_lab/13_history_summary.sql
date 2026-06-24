-- Databricks Data Analyst Medi
-- Query Insights lab / 13 - Query history summary by demo tag
-- ==========================================================
-- Debrief table after running the workload. The avg_shuffle_mb column makes the
-- 08 shuffle join vs 09 broadcast join difference obvious at a glance.

/* QI_DEMO_HISTORY_SUMMARY */
SELECT
  query_tags['demo'] AS demo,
  COUNT(*) AS executions,
  ROUND(AVG(total_duration_ms), 0) AS avg_total_ms,
  MAX(total_duration_ms) AS max_total_ms,
  ROUND(AVG(execution_duration_ms), 0) AS avg_execution_ms,
  ROUND(AVG(read_rows), 0) AS avg_read_rows,
  ROUND(AVG(read_bytes / 1024 / 1024), 2) AS avg_read_mb,
  ROUND(AVG(shuffle_read_bytes / 1024 / 1024), 2) AS avg_shuffle_mb,
  MAX(spilled_local_bytes) AS max_spilled_local_bytes,
  SUM(CASE WHEN from_result_cache THEN 1 ELSE 0 END) AS result_cache_hits
FROM system.query.history
WHERE start_time >= current_timestamp() - INTERVAL 2 HOURS
  AND query_tags['course'] = 'databricks_data_analyst_medi'
GROUP BY query_tags['demo']
ORDER BY max_total_ms DESC;
