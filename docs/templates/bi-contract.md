# BI Contract

## Dataset

- Name:
- Source table/view:
- Grain:
- Refresh owner:
- Business owner:
- Technical owner:

## Tables

| Object | Role | Grain | Refresh pattern | Notes |
|---|---|---|---|---|
| `gold.fact_sales_dashboard` | fact/reporting table | one row per order line | daily | filtered to BI-ready fields |
| `gold.fact_sales_dashboard_monthly` | aggregate | month/category/region | daily | preferred for summary pages |

## Measures

| Measure | Preferred location | Definition |
|---|---|---|
| Revenue | Databricks | `SUM(line_revenue)` |
| Gross margin | Databricks | `SUM(line_margin)` |

## Power BI mode decision

- Baseline:
- When Import is enough:
- When live/DirectQuery is justified:
- Cost guardrails:
