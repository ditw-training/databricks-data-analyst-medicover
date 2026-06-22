# Implementation report v1

## Zakres wykonany

Zaimplementowano pierwszy roboczy build szkolenia `Databricks-Data-Analyst-Medi`
zgodnie z analiza przed implementacja.

## Artefakty

### Foundation

- `setup/00_pre_config.ipynb`
- `setup/00_setup.ipynb`
- `data/generate_training_dataset.ipynb`
- `data/source_csv/Customers.csv`
- `data/source_csv/Product.csv`
- `data/source_csv/ProductCategory.csv`

Generator danych tworzy syntetyczny scenariusz RetailHub oraz kontrolowane
problemy jakosci:

- brakujace ceny,
- statusy spoza slownika,
- przyszle daty,
- duplikaty wybranych linii,
- dane pod walidacje KPI.

### Notebooki modulowe

- `notebooks/m1_sql_warehouse_notebooks.ipynb`
- `notebooks/m2_gold_kpi_best_practices.ipynb`
- `notebooks/m3_powerbi_semantic_dataset.ipynb`
- `notebooks/m4_performance_automation_cicd_orientation.ipynb`

### Warsztaty

- `workshops/w1_gold_kpi_exercise.ipynb`
- `workshops/w1_gold_kpi_solution.ipynb`
- `workshops/w2_powerbi_dataset_exercise.ipynb`
- `workshops/w2_powerbi_dataset_solution.ipynb`

### Wizualizacje osadzone w notebookach

- `assets/images/medallion_to_powerbi.png`
- `assets/images/kimball_gold_model.png`
- `assets/images/powerbi_report_mockup.png`
- `assets/images/import_vs_directquery.png`
- `assets/images/sql_warehouse_cost_decision.png`
- `assets/images/lakeflow_job_dag.png`
- `assets/images/dabs_deployment_flow.png`
- `assets/images/retailhub_source_map.png`
- `assets/images/gold_business_value.png`
- `assets/images/star_schema_vs_flat_table.png`
- `assets/images/kpi_definition_flow.png`
- `assets/images/gold_quality_gate.png`
- `assets/images/powerbi_connection_walkthrough.png`
- `assets/images/incremental_refresh_range.png`
- `assets/images/query_profile_reading_map.png`
- `assets/images/automation_readiness_checklist.png`
- `assets/images/workshop_success_criteria.png`

### Screenshoty przeniesione z bazowego `Databricks-Data-Analyst`

- `assets/images/source_sql_editor.png`
- `assets/images/source_catalog_explorer_hierarchy.png`
- `assets/images/source_catalog_explorer_lineage.png`
- `assets/images/source_powerbi_directquery_connector.webp`

Wizualizacje sa generowane w stylu whiteboard/sketch zblizonym do assetow z
`databricks-data-engineer-associate`: jasne papierowe tlo, szkicowe ramki,
reczna typografia i oszczedne akcenty kolorystyczne.

Pelny indeks obrazow znajduje sie w `docs/07-visual-materials-map.md`.

### Szablony produkcyjne

- `docs/templates/kpi-dictionary.md`
- `docs/templates/bi-contract.md`
- `docs/templates/decision-log.md`
- `docs/templates/refresh-strategy.md`
- `docs/templates/report-certification-checklist.md`
- `docs/templates/data-quality-checklist.md`
- `docs/templates/cost-awareness-checklist.md`

### Automatyzacja / CI-CD

- `bundle/databricks.yml` - referencyjny przyklad DABs / Declarative Automation
  Bundles dla joba `refresh_gold_bi_dataset`.

## Walidacja wykonana lokalnie

- Wszystkie notebooki sa poprawnym JSON.
- Wszystkie niemagiczne komorki Python kompiluja sie lokalnie.
- 21 assetow obrazowych otwiera sie poprawnie lokalnie.
- Generowane obrazy PNG maja rozmiar 1600 x 900.
- Zweryfikowano wizualnie mockup raportu Power BI.
- Zweryfikowano wizualnie styl `medallion_to_powerbi.png` i
  `powerbi_report_mockup.png` po zmianie na whiteboard/sketch.
- Zweryfikowano wizualnie nowe diagramy `retailhub_source_map.png`,
  `powerbi_connection_walkthrough.png` i `query_profile_reading_map.png`.

## Swiadome ograniczenia

- Notebooki nie byly jeszcze uruchomione w realnym Databricks workspace.
- Screenshot z oficjalnego pricingu nie zostal zapisany jako finalny asset.
  Obecnie istnieje `sql_warehouse_cost_decision.png`; screenshot pricingu trzeba
  odswiezyc przed dostarczeniem szkolenia.
- `bundle/databricks.yml` jest przykladem referencyjnym i powinien zostac
  zweryfikowany z aktualna wersja Databricks CLI przed live demo.

## Rekomendowany test live

1. Import folderu `Databricks-Data-Analyst-Medi` do Databricks Workspace.
2. Run `setup/00_pre_config.ipynb`.
3. Run `data/generate_training_dataset.ipynb`.
4. Run kolejno:
   - `notebooks/m1_sql_warehouse_notebooks.ipynb`
   - `notebooks/m2_gold_kpi_best_practices.ipynb`
   - `workshops/w1_gold_kpi_solution.ipynb`
   - `notebooks/m3_powerbi_semantic_dataset.ipynb`
   - `workshops/w2_powerbi_dataset_solution.ipynb`
   - `notebooks/m4_performance_automation_cicd_orientation.ipynb`
5. Sprawdzic, czy wszystkie obrazy renderuja sie w markdown notebookow.
