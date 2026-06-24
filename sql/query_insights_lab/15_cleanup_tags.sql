-- Databricks Data Analyst Medi
-- Query Insights lab / 15 - Cleanup
-- =================================
-- Run last. Unsets the session query tags and restores the broadcast threshold
-- in case you keep using the same SQL Editor session for other work.

SET spark.sql.autoBroadcastJoinThreshold = 10485760;

SET QUERY_TAGS['course'] = UNSET,
    QUERY_TAGS['module'] = UNSET,
    QUERY_TAGS['trainer_demo'] = UNSET,
    QUERY_TAGS['demo'] = UNSET;
