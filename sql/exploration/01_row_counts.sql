-- Day 1 SQL Editor demo: RetailHub source discovery
-- 01 - Row counts across Silver tables
-- ==================================================
-- Expected observation: customers/products are master data;
-- orders/lines are transactional.

USE SCHEMA silver;

SELECT 'customers' AS table_name, COUNT(*) AS rows FROM customers
UNION ALL
SELECT 'products', COUNT(*) FROM products
UNION ALL
SELECT 'sales_orders', COUNT(*) FROM sales_orders
UNION ALL
SELECT 'order_lines', COUNT(*) FROM order_lines
ORDER BY table_name;
