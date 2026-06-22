# Data Quality Checklist

| Rule | Query/object | Threshold | Status |
|---|---|---|---|
| No duplicate order lines | `line_id` uniqueness | 0 duplicates | TODO |
| Valid statuses only | status dictionary | 0 invalid | TODO |
| No missing product/customer links | FK checks | 0 orphans | TODO |
| No future orders | order_date <= current_date | 0 rows | TODO |
| Price and cost present | unit_price/unit_cost | > 99% complete | TODO |
