# Struktura szkolenia

## Docelowy uklad katalogow

```text
Databricks-Data-Analyst-Medi/
├── docs/
│   ├── agenda-source.md
│   ├── 00-agenda-analysis.md
│   ├── 01-training-structure.md
│   ├── 02-master-training-plan.md
│   ├── 03-source-material-map.md
│   ├── 04-pre-implementation-analysis.md
│   ├── TRAINER_GUIDE.md
│   └── build-log.md
├── setup/
│   ├── 00_pre_config.ipynb
│   └── 00_setup.ipynb
├── data/
│   ├── generate_training_dataset.ipynb
│   └── source_csv/
├── notebooks/
│   ├── m1_sql_warehouse_notebooks.ipynb
│   ├── m2_gold_kpi_best_practices.ipynb
│   ├── m3_powerbi_semantic_dataset.ipynb
│   └── m4_performance_automation_cicd_orientation.ipynb
├── workshops/
│   ├── w1_gold_kpi_exercise.ipynb
│   ├── w1_gold_kpi_solution.ipynb
│   ├── w2_powerbi_dataset_exercise.ipynb
│   └── w2_powerbi_dataset_solution.ipynb
├── presentation/
│   ├── m1_sql_warehouse_notebooks.pptx
│   ├── m2_gold_kpi_best_practices.pptx
│   ├── m3_powerbi_semantic_dataset.pptx
│   └── m4_performance_automation_cicd_orientation.pptx
├── scripts/
│   ├── notebooks/
│   ├── workshops/
│   └── presentation/
├── tools/
└── assets/images/
```

## Mapa agendy na materialy

| Blok | Czas | Materialy | Cel |
|---|---:|---|---|
| Foundation | przed szkoleniem | `setup/*`, `data/*` | przygotowanie katalogu, schematow i danych |
| Modul 1: SQL Warehouse, pricing + Notebooks | ok. 45 min | `m1_sql_warehouse_notebooks` + pricing visual | szybkie wejscie w prace analityczna i koszty warehouse |
| Modul 2: Medallion, Gold/KPI/Kimball | ok. 90 min | `m2_gold_kpi_best_practices` + deck/visuals | zbudowanie poprawnego kontraktu KPI i Gold layer |
| Warsztat 1: KPI w Gold | ok. 75 min | `w1_gold_kpi_*` | praktyczne tabele Gold i walidacja KPI |
| Modul 3: Power BI Import + Live | ok. 90 min | `m3_powerbi_semantic_dataset` + mockup raportu | dataset, semantyka, Import vs live connection |
| Warsztat 2: dataset Power BI | ok. 45 min | `w2_powerbi_dataset_*` | gotowosc danych do raportu i incremental refresh |
| Modul 4: koszty/performance/Jobs/DABs | ok. 75 min | `m4_performance_automation_cicd_orientation` + visuals | koszt, automatyzacja i CI/CD decyzyjnie |

## Kontrakt danych

Startowo zakladamy wykorzystanie kontraktu z `Databricks-Data-Analyst`:

- `silver.customers`
- `silver.products`
- `silver.sales_orders`
- `silver.order_lines`
- `gold.dim_date`
- `gold.dim_product`
- `gold.dim_customer`
- `gold.fact_sales`
- `gold.kpi_daily`
- `gold.revenue_monthly`

Wersja Medi moze zachowac ten kontrakt albo zmienic nazwy/scenariusz biznesowy
po decyzji wlasciciela materialow.

## Zasady budowy

- Materialy w notebookach po polsku.
- Nazwy plikow po angielsku, spojne z kursem bazowym.
- Kazdy modul ma czesc podstawowa oraz opcjonalna sekcje bonusowa.
- Warsztaty maja osobny notebook `exercise` i `solution`.
- Klasyczne prezentacje sa opcjonalne; priorytetem sa wizualizacje, mockupy i
  screenshoty osadzone w notebookach lub krotkich visual decks.
- Modul 4 pozostaje orientacyjny: pokazuje decyzje i antywzorce, ale nie buduje
  pelnego pipeline ani procesu CI/CD.

## Kolejnosc kolejnych prac

0. Potwierdzic decyzje z `docs/04-pre-implementation-analysis.md`.
1. Skopiowac i odchudzic foundation: setup oraz generator danych.
2. Zbudowac notebook modulu 1 i pricing/cost visual.
3. Zbudowac modul 2 oraz warsztat 1.
4. Zbudowac modul 3 oraz warsztat 2.
5. Zbudowac modul 4 orientacyjny.
6. Uruchomic QA statyczne notebookow, wizualizacji i opcjonalnych deckow.
7. Dopiero potem wykonac test w realnym workspace Databricks.
