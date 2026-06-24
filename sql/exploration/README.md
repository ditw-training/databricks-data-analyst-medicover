# Day 1 SQL Editor demo: RetailHub source discovery

How analysts explore governed **Silver** tables before any Gold modeling starts.
Split into small, single-purpose files so each one opens as its own SQL Editor
query and runs one section at a time.

## How to run in SQL Editor

1. Open Databricks SQL Editor.
2. Open one file at a time as a new query.
3. Select your participant catalog manually in the catalog dropdown
   (example: `retailhub_jan_kowalski`). The files only set the schema with
   `USE SCHEMA silver;`.
4. Select a SQL Warehouse.
5. Create the query parameters listed below.
6. Run the section.

## Query parameters to create

| Name         | Type   | Value       |
|--------------|--------|-------------|
| p_status     | Text   | Completed   |
| p_start_date | Date   | 2024-01-01  |
| p_end_date   | Date   | 2024-12-31  |
| p_channel    | Text   | All         |
| p_top_n      | Number | 10          |

Databricks SQL named parameters use `:parameter_name`, e.g.
`WHERE status = :p_status`. Use `p_channel = All` to skip the channel filter.

## Run order

| File                              | Purpose                                              |
|-----------------------------------|------------------------------------------------------|
| `00_session_setup.sql`            | Set catalog/schema and confirm SQL context.          |
| `01_row_counts.sql`               | Row counts across Silver tables.                     |
| `02_order_header_grain.sql`       | Order header grain and date range.                   |
| `03_order_line_grain.sql`         | Order line grain.                                    |
| `04_status_distribution.sql`      | Status distribution.                                 |
| `05_status_channel_param.sql`     | Parameterized status + channel query.                |
| `06_revenue_by_channel.sql`       | Parameterized date-window revenue by channel.        |
| `07_top_n_products.sql`           | Top-N products by revenue.                           |
| `08_source_risk_register.sql`     | Source modeling risks to document before Gold.       |
| `09_header_vs_lines_recon.sql`    | Header-vs-lines reconciliation sample.               |

## Training rule

SQL Editor is for fast exploration and saved analyst queries. Repeatable course
checks are reproduced in the notebook with `%sql` cells.
