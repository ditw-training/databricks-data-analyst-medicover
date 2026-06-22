# KPI Dictionary

| KPI | Business definition | SQL definition | Grain | Default filters | Owner | Caveats |
|---|---|---|---|---|---|---|
| Revenue | Completed order line revenue after discount | `SUM(line_revenue)` | order line | `status = 'Completed'` | Sales Ops | Excludes cancelled and returned lines |
| Gross margin | Revenue minus line cost | `SUM(line_margin)` | order line | `status = 'Completed'` | Finance | Requires product cost |
| Return rate | Returned orders divided by completed + returned orders | `returned_orders / eligible_orders` | order | rolling period | Sales Ops | Sensitive to status mapping |

## Trainer note

During the workshop participants fill at least three KPI rows and add one caveat
per KPI.
