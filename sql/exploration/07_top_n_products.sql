-- Day 1 SQL Editor demo: RetailHub source discovery
-- 07 - Top-N products by revenue
-- ==================================================
-- Change p_top_n in SQL Editor and rerun.

USE SCHEMA silver;

WITH product_revenue AS (
  SELECT
    product_id,
    category,
    ROUND(SUM(line_revenue), 2) AS revenue
  FROM order_lines
  WHERE status = :p_status
    AND order_date BETWEEN CAST(:p_start_date AS DATE) AND CAST(:p_end_date AS DATE)
    AND (:p_channel = 'All' OR channel = :p_channel)
  GROUP BY product_id, category
),
ranked AS (
  SELECT
    product_id,
    category,
    revenue,
    DENSE_RANK() OVER (ORDER BY revenue DESC) AS revenue_rank
  FROM product_revenue
)
SELECT
  revenue_rank,
  product_id,
  category,
  revenue
FROM ranked
WHERE revenue_rank <= CAST(:p_top_n AS INT)
ORDER BY revenue_rank, product_id;
