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

## Medi Block 1 — Foundation pre-checks (FND-01..04, GLOBAL-01)

Zaimplementowano w `scripts/build_materials_v1.py`, funkcja
`notebook_data_generator()` (`data/generate_training_dataset.ipynb`), oraz
nowy generyczny helper `precheck_cell()` obok `md_cell`/`code_cell`.

**FND-01 — runtime pre-check po generatorze.** Dodano 3 komorki na koncu
notebooka: (a) `spark.catalog.tableExists` dla wszystkich 10 tabel
Silver+Gold, (b) `assert` na minimalnej liczbie wierszy per tabela, (c) 7
assercji potwierdzajacych, ze kontrolowane problemy jakosci faktycznie
istnieja w danych: brakujace `unit_price`, status spoza slownika, zamowienie
z data w przyszlosci, duplikat `(order_id, product_id)`, orphan
`customer_id`, orphan `product_id`, mismatch header-vs-lines.

**FND-02 — jawny data contract.** Dodano markdown z tabela
`Obiekt | Grain | Klucze | Właściciel` dla wszystkich 10 obiektow
Silver/Gold, plus 2 komorki `DESCRIBE TABLE` dla `gold.fact_sales` i
`gold.dim_date`.

**FND-03 — rozszerzony bad data lab.** Dodano: (a) orphan `customer_id` (co
4001-szy `line_id`) i orphan `product_id` (co 3001-szy `line_id`) wskazujace
na wartosci spoza zakresu wymiarow; (c) potwierdzono, ze istniejacy
mechanizm duplikatow (`line_id % 10007 = 0`, re-insert z nowym `line_id`)
jest faktycznym duplikatem na parze `(order_id, product_id)`, nie tylko
near-duplicate — dodano jawna asercje.

Decyzja projektowa (b) — revenue mismatch: schemat `silver.sales_orders`
(header) nie mial wczesniej zadnego pola total. Zamiast dodawac sztuczny
markdown "nie dotyczy", dodano minimalna, uzasadniona biznesowo kolumne
`order_total_amount` w `silver.sales_orders`, liczona jako suma
`line_revenue` z `silver.order_lines` dla danego zamowienia. Dla wiekszosci
zamowien wartosc sie zgadza (rekoncyliuje). Dla zamowien gdzie
`order_id % 401 = 0` header total jest celowo zawyzony o staly 50.0,
symulujac nieaktualny/błędnie wprowadzony total z systemu źródłowego. To
czyni check `ABS(header - SUM(lines)) > 0.01` sensownym cwiczeniem
reconciliation zamiast pustego placeholdera.

**FND-04 — table comments.** Dodano `COMMENT ON TABLE` dla 4 tabel Silver
(`saveAsTable`, wiec `COMMENT ON TABLE` po zapisie) oraz `COMMENT '...'`
inline w `CREATE OR REPLACE TABLE ... AS SELECT` dla wszystkich 6 obiektow
Gold. Dodano markdown notke, ze `COMMENT ON COLUMN` to nice-to-have do
dodania pozniej, jesli docelowy runtime/warehouse to wspiera — blok
ogranicza sie do table-level comments (uniwersalnie wspierane).

**GLOBAL-01 — reusable pre-check helper.** Nowa funkcja
`precheck_cell(required_tables, prereq_notebook)` w
`scripts/build_materials_v1.py` generuje standardowa komorke: sprawdza
`spark.catalog.tableExists` dla kazdej tabeli, przy braku wypisuje czytelny
komunikat z nazwa notebooka-prerequisite i rzuca wyjatek. Uzyta w
`notebook_data_generator()` jako self-check na koncu (sprawdza 6 obiektow
Gold po ich utworzeniu). W komentarzu w kodzie udokumentowano plan reuse w
`notebook_module_2/3/4` i `notebook_workshop_1/2` w kolejnym bloku — nie
zaimplementowano tam jeszcze, poza zakresem tego bloku.

### Weryfikacja

```
.venv/bin/python scripts/build_materials_v1.py
# -> "Built Databricks-Data-Analyst-Medi v1 materials" (bez bledow)

nbformat.read(as_version=4) + nbformat.validate(): PASS
data/generate_training_dataset.ipynb: 24 cells (10 markdown, 14 code)
Niemagiczne komorki Python skompilowane: 13/13 OK (1 magic %run pominieta)

Walidacja WSZYSTKICH notebookow w repo (nbformat + compile): 11/11 PASS
(data/generate_training_dataset.ipynb, m1-m4, setup x2, w1/w2 exercise+solution)
```

Grep proof: markdown z tabela data contract obecny, `COMMENT ON TABLE`
(4x Silver) i `COMMENT '...'` (6x Gold CTAS, lacznie 9+ wystapien `COMMENT '`
licząc helper-markdown), orphan reference checks (`LEFT ANTI JOIN` x2),
revenue mismatch (`order_total_amount`, `revenue_mismatch_count`), exact
duplicate (`exact_dup_count`, `HAVING COUNT`), 9x `assert` w FND-01 blokach,
`precheck_cell` zdefiniowany raz i wywolany raz w generatorze.
