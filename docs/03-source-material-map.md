# Mapa materialow zrodlowych

Ten dokument wskazuje, skad brac tresci do budowy `Databricks-Data-Analyst-Medi`.
Nie kopiujemy wszystkiego jeden do jednego. Wybieramy fragmenty, ktore pasuja do
7-godzinnego szkolenia analitycznego.

## Databricks-Data-Analyst

Glowne zrodlo dla:

- SQL Warehouse,
- Gold layer,
- Kimball / model gwiazdy,
- Power BI model,
- Import vs DirectQuery,
- query performance pod BI,
- visual BI connection screenshot.

Najwazniejsze pliki:

- `Databricks-Data-Analyst/notebooks/m2a_lakehouse_dw_overview.ipynb`
- `Databricks-Data-Analyst/notebooks/m2c_kimball_dimensional.ipynb`
- `Databricks-Data-Analyst/notebooks/m2e_medallion_metric_views.ipynb`
- `Databricks-Data-Analyst/notebooks/m3a_powerbi_modelling_connection.ipynb`
- `Databricks-Data-Analyst/notebooks/m3b_powerbi_performance_live_demo.ipynb`
- `Databricks-Data-Analyst/notebooks/m4d_query_analysis_photon.ipynb`
- `Databricks-Data-Analyst/notebooks/m4f_best_practices_sql_analytics.ipynb`
- `Databricks-Data-Analyst/assets/images/powerbi_directquery_connector.webp`

## Databricks Lakehouse & Transformation

Glowne zrodlo dla:

- Medallion Architecture,
- Lakeflow Pipelines,
- Lakeflow Jobs,
- kosztow compute/storage,
- optimization and maintenance,
- SQL Warehouse vs Job Compute,
- DABs jako YAML dla jobow.

Najwazniejsze pliki:

- `Databricks Lakehouse & Transformation/README.md`
- `Databricks Lakehouse & Transformation/SYLLABUS.md`
- `Databricks Lakehouse & Transformation/notebooks/Day1/Demo/01_medallion_architecture_demo.ipynb`
- `Databricks Lakehouse & Transformation/notebooks/Day1/Demo/04_orchestration_demo.ipynb`
- `Databricks Lakehouse & Transformation/notebooks/Day2/Demo/03_cost_management_demo.ipynb`
- `Databricks Lakehouse & Transformation/materials/medallion/`
- `Databricks Lakehouse & Transformation/materials/orchestration/`
- `Databricks Lakehouse & Transformation/materials/lakeflow/lakeflow_demo/`

## databricks-data-engineer-associate

Glowne zrodlo dla:

- Lakeflow Jobs,
- CI/CD,
- DABs,
- medallion pipeline,
- Power BI DirectQuery live demo,
- cost/performance notes.

Najwazniejsze pliki:

- `databricks-data-engineer-associate/README.md`
- `databricks-data-engineer-associate/notebooks/day2/demo/06_medallion_architecture.ipynb`
- `databricks-data-engineer-associate/notebooks/day3/demo/08_job_orchestration.ipynb`
- `databricks-data-engineer-associate/notebooks/day3/demo/09_cicd_and_automation.ipynb`
- `databricks-data-engineer-associate/notebooks/day3/lab/lab_08_orchestration.ipynb`
- `databricks-data-engineer-associate/notebooks/bonus/BONUS_powerbi_direct_query.ipynb`
- `databricks-data-engineer-associate/materials/medallion/`
- `databricks-data-engineer-associate/materials/orchestration/`

## dbx-ana archive

Stary `dbx-ana` jest przydatny jako lekki, bliski agendzie szkic 7h:

- `dbx-ana/session-2-powerbi-performance/s2_m4_performance_cost.ipynb`
- `dbx-ana/session-3-automation-cicd/s3_m5a_jobs_pipelines.ipynb`
- `dbx-ana/session-3-automation-cicd/s3_m5b_cicd_dabs.ipynb`
- `dbx-ana/session-3-automation-cicd/databricks.yml`

Uwaga: przed uzyciem trzeba sprawdzic aktualnosc terminologii, bo Databricks
zmienia nazwy produktow, np. Databricks Asset Bundles -> Declarative Automation
Bundles w najnowszej dokumentacji.

## Oficjalne zrodla Databricks

Do tematow zmiennych w czasie uzywamy oficjalnych stron i dokumentacji:

- Pricing overview: `https://www.databricks.com/product/pricing`
- Pricing calculator: `https://www.databricks.com/product/pricing/product-pricing/instance-types`
- Declarative Automation Bundles: `https://docs.databricks.com/aws/en/dev-tools/bundles/`
- Lakeflow Jobs: `https://docs.databricks.com/aws/en/jobs/`
- Power BI with Databricks: `https://docs.databricks.com/aws/en/partners/bi/power-bi`

Zasada: ceny, screenshoty pricingu i aktualne nazwy produktow weryfikujemy
bezposrednio przed finalnym wygenerowaniem materialow.

