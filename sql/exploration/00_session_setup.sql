-- Day 1 SQL Editor demo: RetailHub source discovery
-- 00 - Session setup
-- ==================================================
-- Run this first. Sets the schema and confirms the SQL context.
-- Select the catalog manually in the SQL Editor catalog dropdown.
-- Create the SQL Editor parameters listed in README.md before running 05+.

USE SCHEMA silver;

-- Confirm current SQL context.
-- Expected observation: catalog = your participant catalog, schema = silver.
SELECT
  current_user()    AS current_user,
  current_catalog() AS catalog_name,
  current_schema()  AS schema_name;
