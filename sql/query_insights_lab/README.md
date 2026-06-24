# Query Insights / Query Profile / Optimization lab

This lab is split into small, single-purpose SQL files so each one can be opened
as its own query in the Databricks SQL Editor and inspected separately in
**Query History -> Query Profile**.

## Prerequisites

1. Run `setup/00_setup.ipynb`.
2. Run Workshop 1 solution: `notebooks/workshops/solution/w1_gold_kpi_solution.ipynb`.
3. Run Workshop 2 solution: `notebooks/workshops/solution/w2_powerbi_dataset_solution.ipynb`.
4. Select the participant catalog manually in the SQL Editor catalog dropdown
   (the files only set the schema with `USE SCHEMA gold;`).

## SQL Editor parameters to create

| Name        | Type      | Value                 |
|-------------|-----------|-----------------------|
| p_start_ts  | Timestamp | 2024-01-01 00:00:00   |
| p_end_ts    | Timestamp | 2025-01-01 00:00:00   |
| p_start_dt  | Date      | 2024-01-01            |
| p_end_dt    | Date      | 2025-01-01            |
| p_region    | Text      | All                   |
| p_category  | Text      | All                   |
| p_top_n     | Number    | 10                    |

## Run order

| File                                   | Purpose                                                   |
|----------------------------------------|-----------------------------------------------------------|
| `00_session_setup.sql`                 | Set catalog/schema and session query tags. Run first.     |
| `01_precheck.sql`                      | Confirm serving objects exist and have data.              |
| `02_detail_scan.sql`                   | Heavy line-grain aggregation (baseline).                  |
| `03_serving_aggregate.sql`             | Optimized pre-aggregated equivalent.                      |
| `04_antipattern_date_function.sql`     | Function-on-column anti-pattern.                          |
| `05_optimized_range_predicate.sql`     | Range-predicate + serving-grain fix.                      |
| `06_explain_detail.sql`                | `EXPLAIN FORMATTED` for the detail scan.                  |
| `07_explain_aggregate.sql`             | `EXPLAIN FORMATTED` for the serving aggregate.            |
| `08_shuffle_join.sql`                  | **Shuffle (sort-merge) join** — high shuffle bandwidth.   |
| `09_broadcast_join.sql`                | **Broadcast join** — same result, little/no shuffle.      |
| `10_delta_metadata.sql`                | `DESCRIBE DETAIL` / `DESCRIBE HISTORY`.                   |
| `11_optimize_vacuum.sql`               | `OPTIMIZE` and `VACUUM ... DRY RUN`.                      |
| `12_history_lookup.sql`                | Per-statement query history for this lab.                 |
| `13_history_summary.sql`               | Debrief table aggregated by demo tag.                     |
| `14_slow_query_finder.sql`             | General slow-query finder for the current user.           |
| `15_cleanup_tags.sql`                  | Unset the session query tags. Run last.                   |

## Teaching flow

- **A.** Run `00`-`05` to generate a profileable workload, then compare
  `QI_DEMO_01` vs `QI_DEMO_02` in Query History.
- **B.** Run `06`-`07` to read physical plans before running large variants.
- **C.** Run `08` then `09` and open both in Query Profile. Compare the
  **Shuffle** stage and `shuffle_read_bytes` / `shuffle_write_bytes`: the
  sort-merge join shuffles both sides across the network (high bandwidth), the
  broadcast join ships only the small dimension once.
- **D.** Run `10`-`11` for table metadata and maintenance.
- **E.** Run `12`-`14` if you have access to `system.query.history`, otherwise
  use the Query History UI and filter by the `QI_DEMO_*` text comments.
- **F.** Run `15` to clean up tags.

## Notes

- Query tags are Databricks SQL Public Preview. If unavailable, comment out the
  `SET QUERY_TAGS` statements and filter Query History by the query-text
  comments such as `QI_DEMO_01_DETAIL_SCAN`.
- `system.query.history` is usually admin-controlled. If you cannot query it,
  use the Query History UI instead.
- The `SET spark.sql.autoBroadcastJoinThreshold` statements in `08`/`09` are
  session settings on a SQL Warehouse. They are reset in `09` and again in
  `15`; if a warehouse blocks them, use the `/*+ SHUFFLE_MERGE */` and
  `/*+ BROADCAST */` hints (already present) instead.
