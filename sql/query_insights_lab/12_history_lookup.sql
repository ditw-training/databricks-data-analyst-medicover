-- Databricks Data Analyst Medi
-- Query Insights lab / 12 - Query history lookup (per statement)
-- =============================================================
-- Requires access to system.query.history. If statement_text is redacted, use
-- query_tags + statement_id and open the statement in the Query History UI.
-- Note shuffle_read_bytes / spilled_local_bytes for the 08 vs 09 join demos.

SET QUERY_TAGS['demo'] = '09_history_lookup';

/* QI_DEMO_09_HISTORY_LOOKUP */
SELECT
  start_time,
  end_time,
  statement_id,
  executed_by,
  client_application,
  compute.type AS compute_type,
  compute.warehouse_id AS warehouse_id,
  execution_status,
  query_tags['demo'] AS demo,
  total_duration_ms,
  waiting_for_compute_duration_ms,
  waiting_at_capacity_duration_ms,
  compilation_duration_ms,
  execution_duration_ms,
  total_task_duration_ms,
  read_rows,
  produced_rows,
  ROUND(read_bytes / 1024 / 1024, 2) AS read_mb,
  read_files,
  pruned_files,
  shuffle_read_bytes,
  spilled_local_bytes,
  from_result_cache,
  LEFT(statement_text, 160) AS statement_preview
FROM system.query.history
WHERE start_time >= current_timestamp() - INTERVAL 2 HOURS
  AND query_tags['course'] = 'databricks_data_analyst_medi'
ORDER BY start_time DESC;
