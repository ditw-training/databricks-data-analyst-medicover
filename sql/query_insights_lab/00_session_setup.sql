-- Databricks Data Analyst Medi
-- Query Insights lab / 00 - Session setup
-- =======================================
-- Run this first in the SQL Editor session. It sets the schema and the
-- session query tags that make the lab statements easy to find later in
-- Query History and system.query.history.
--
-- Select the catalog manually in the SQL Editor catalog dropdown.
-- Create the SQL Editor parameters listed in README.md before running 01+.

USE SCHEMA gold;

-- Session tags for Query Insights / system.query.history.
SET QUERY_TAGS['course'] = 'databricks_data_analyst_medi',
    QUERY_TAGS['module'] = 'query_insights_optimization',
    QUERY_TAGS['trainer_demo'] = 'true';

-- Confirm context.
SELECT
  current_user()    AS current_user,
  current_catalog() AS catalog_name,
  current_schema()  AS schema_name;
