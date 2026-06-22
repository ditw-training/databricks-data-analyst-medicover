# Build Log

## 2026-06-22 - start

- Utworzono szkielet projektu `Databricks-Data-Analyst-Medi`.
- Przeanalizowano istniejacy `Databricks-Data-Analyst`.
- Przyjeto, ze wersja Medi jest skondensowana sciezka 7h, a nie kopia calego
  kursu bazowego.
- Utworzono dokumenty:
  - `docs/agenda-source.md`
  - `docs/00-agenda-analysis.md`
  - `docs/01-training-structure.md`
  - `docs/TRAINER_GUIDE.md`

## 2026-06-22 - master plan

- Dodano `docs/02-master-training-plan.md` jako glowny dokument planistyczny.
- Rozszerzono koncepcje szkolenia o:
  - jeden scenariusz biznesowy end-to-end,
  - bad data lab,
  - KPI dictionary,
  - data quality score,
  - incident scenario,
  - before/after performance,
  - BI contract,
  - report certification checklist,
  - capstone,
  - wizualizacje techniczne i mockupy dashboardow.
- Przyjeto, ze klasyczne prezentacje sa opcjonalne; jesli powstana, powinny byc
  krotkimi wizualnymi deckami, a nie slajdami tekstowymi.

## 2026-06-22 - wymagania wlasciciela

- Dopisano do master planu wymagania:
  - pricing i koszty SQL Warehouse z aktualnym screenshotem/assetem,
  - Medallion Architecture, Gold layer i Kimball-style Gold demo,
  - realny business case dla analizy w Gold layer,
  - model budowany w Databricks, Power BI jako cienka warstwa,
  - dwa tryby Power BI: Import oraz live connection / DirectQuery,
  - mockup raportu Power BI w PNG,
  - automatyzacja przez Lakeflow Jobs,
  - CI/CD przez DABs / Declarative Automation Bundles.
- Dodano `docs/03-source-material-map.md` z lokalnymi i oficjalnymi zrodlami do
  wykorzystania przy budowie materialow.

## 2026-06-22 - analiza przed implementacja

- Dodano `docs/04-pre-implementation-analysis.md` jako ostatni checkpoint przed
  budowa materialow.
- Ustalono roboczy produkt v1: `RetailHub Executive KPI Dashboard`.
- Zamknieto zakres v1 i zakres poza v1.
- Zdefiniowano docelowy pakiet uczestnika, gold standard raportu, assety
  wizualne, kolejnosc implementacji i kryteria akceptacji.
- Rekomendowany pierwszy milestone: foundation, templates, kontrolowane problemy
  jakosci, mockup raportu i diagram Medallion -> Power BI.

## 2026-06-22 - implementacja v1

- Dodano generator materialow `scripts/build_materials_v1.py`.
- Wygenerowano foundation:
  - `setup/00_pre_config.ipynb`
  - `setup/00_setup.ipynb`
  - `data/generate_training_dataset.ipynb`
  - referencyjne CSV w `data/source_csv/`
- Wygenerowano notebooki modulowe `m1`-`m4`.
- Wygenerowano warsztaty `w1` i `w2` w wariantach `exercise` i `solution`.
- Wygenerowano assety wizualne PNG osadzone w notebookach:
  - Medallion -> Power BI
  - Kimball Gold model
  - Power BI report mockup
  - Import vs DirectQuery
  - SQL Warehouse cost decision
  - Lakeflow Job DAG
  - DABs deployment flow
- Dodano szablony dokumentow w `docs/templates/`.
- Dodano referencyjny `bundle/databricks.yml`.
- Walidacja lokalna:
  - notebooki sa poprawnym JSON,
  - niemagiczne komorki Python kompilują sie lokalnie,
  - obrazy PNG maja rozmiar 1600 x 900.
- Dodano `docs/05-implementation-report.md`.

## 2026-06-22 - styl wizualizacji

- Przebudowano generator assetow PNG, aby wizualizacje byly blizsze stylowi
  `databricks-data-engineer-associate`.
- Zmieniono bazowy styl obrazow na whiteboard/sketch:
  - jasne papierowe tlo,
  - szkicowe obramowania,
  - reczna typografia,
  - delikatna tekstura,
  - oszczedne akcenty kolorystyczne.
- Przebudowano wszystkie obrazy w `assets/images/`.
- Zweryfikowano lokalnie poprawny JSON notebookow i kompilacje niemagicznych
  komorek Python po regeneracji.

## 2026-06-22 - notebook review

- Przejrzano notebook po notebooku pod katem objetosci, zaleznosci i runtime
  risk.
- Znaleziono i naprawiono dwa krytyczne bledy:
  - `silver.order_lines` nie mial `customer_id`, a `gold.fact_sales` go
    wymagal,
  - `gold.fact_sales_dashboard` nie mial `unit_price`, `unit_cost` i
    `discount_pct`, a data quality check uzywal `unit_price`.
- Potwierdzono, ze obecny material jest za krotki na 7h i wymaga rozbudowy.
- Dodano `docs/06-notebook-review-and-expansion-tasks.md` z backlogiem
  rozbudowy notebook po notebooku.

## 2026-06-22 - rozbudowa wizualna i materialowa

- Rozszerzono generator `scripts/build_materials_v1.py`, aby kopiowal
  przydatne screenshoty z bazowego `Databricks-Data-Analyst`:
  - SQL Editor,
  - Catalog Explorer hierarchy,
  - Catalog Explorer lineage,
  - Power BI DirectQuery connector.
- Dodano nowe whiteboard/sketch assety:
  - RetailHub source map,
  - Gold business value,
  - Star schema vs flat BI table,
  - KPI definition flow,
  - Gold quality gate,
  - Power BI connection walkthrough,
  - Incremental refresh range,
  - Query profile reading map,
  - Automation readiness checklist,
  - Workshop success criteria.
- Rozbudowano notebooki:
  - `m1` ma teraz screenshoty UI, source map, runtime pre-check, risk scan i
    mini-cwiczenie kosztowe,
  - `m2` ma business case, star-vs-flat, kontrole grain, distinct-count trap,
    reconciliation, quality gate i lineage,
  - `m3` ma screenshot konektora Power BI, walkthrough polaczenia, incremental
    refresh i mode-decision matrix,
  - `m4` ma query profile map, optymalizacyjna checkliste, Lakeflow, DABs i
    rozszerzenie do dluzszej dostawy.
- Rozbudowano warsztaty `w1` i `w2` o success criteria, pre-checki, expected
  outputs, self-checki, decyzje i bonusy.
- Dodano `docs/07-visual-materials-map.md` jako indeks assetow i ich uzycia.
- Walidacja lokalna po regeneracji:
  - `python3 -m py_compile scripts/build_materials_v1.py` OK,
  - wszystkie notebooki parsują sie jako JSON,
  - niemagiczne komorki Python kompilują sie lokalnie,
  - 21 assetow obrazowych otwiera sie poprawnie.
