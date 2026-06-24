-- Databricks Data Analyst Medi
-- Query Insights lab / 11 - Maintenance: OPTIMIZE / VACUUM
-- =======================================================
-- OPTIMIZE is safe on a training table but may take a moment.
-- VACUUM DRY RUN does not delete files; it only lists what would be eligible.
-- Run each statement separately. Re-run file 10 after OPTIMIZE to compare numFiles.

USE SCHEMA gold;

SET QUERY_TAGS['demo'] = '08_optimize';

OPTIMIZE gold.fact_sales_dashboard_monthly;

VACUUM gold.fact_sales_dashboard_monthly RETAIN 168 HOURS DRY RUN;

-- Optional, if your workspace supports Z-ORDER and the table is not liquid-clustered:
-- OPTIMIZE gold.fact_sales_dashboard_monthly
-- ZORDER BY (customer_region, category);
