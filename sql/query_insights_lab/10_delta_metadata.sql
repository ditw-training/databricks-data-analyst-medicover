-- Databricks Data Analyst Medi
-- Query Insights lab / 10 - Delta metadata
-- ========================================
-- Use these before/after the OPTIMIZE discussion (file 11).
-- Run each statement separately in the SQL Editor.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '07_delta_metadata';

-- numFiles, sizeInBytes, partitioning / clustering columns.
DESCRIBE DETAIL gold.fact_sales_dashboard_monthly;

-- Commit history: OPTIMIZE / WRITE / MERGE operations and their metrics.
DESCRIBE HISTORY gold.fact_sales_dashboard_monthly;
