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

## Medi Block 2 - Module 2 expansion

Rozbudowa `notebook_module_2()` w `scripts/build_materials_v1.py`
(`m2_gold_kpi_best_practices.ipynb`) wedlug backlog taskow M2-01 do M2-06 z
`docs/06-notebook-review-and-expansion-tasks.md`. 26 -> 36 komorek
(20 markdown, 16 code).

**M2-01 — Medallion explanation.** Dodano tabele porownawcza Bronze/Silver/
Gold (ownership, quality bar, latency, consumers) oraz sekcje "co nie
powinno trafic do Gold" i "Gold vs ad-hoc working view analityka".

**M2-02 — Kimball step-by-step.** Grain zadeklarowany PRZED budowa
(`one row = one order line...`). Dodano recap istniejacych wymiarow
(`dim_date`, `dim_customer`, `dim_product` z generatora — `DESCRIBE TABLE` +
przyklad danych), istniejacy diagram `kimball_gold_model.png` (sprawdzono,
juz byl referencjonowany — bez duplikacji). Zbudowano NOWY obiekt
`gold.fact_sales_dashboard` (denormalizowany, dashboard-ready, odrebny od
`gold.fact_sales` generatora) + `gold.fact_sales_dashboard_monthly`, oba z
`COMMENT`.

**M2-03 — KPI dictionary w notebooku.** Tabela markdown Revenue/Gross
margin/Return rate/Orders/DQ score z business + SQL definition side by
side, nastepnie zapytanie SQL materializujace `kpi_dictionary_snapshot`
temp view jako rzeczywista praca w notebooku (nie tylko referencja do
`docs/templates/kpi-dictionary.md`).

**M2-04 — Reconciliation checks.** Porownanie revenue `gold.fact_sales` vs
`gold.fact_sales_dashboard` (powinny sie zgadzac), reconciliation
detail-vs-aggregate, oraz NOWA sekcja "deliberately bad join (fan-out)" —
join po `category` zamiast `product_id` pokazuje inflacje wierszy/revenue.
Dodano explicit `COUNT(DISTINCT)` pitfall (line-grain count bez DISTINCT
zawyza liczbe zamowien).

**M2-05 — Data quality score breakdown.** Rozszerzono score o
issue_type/severity (high/medium) z penalty_points, leverage Block 1
checks (orphan_customer_id, orphan_product_id, revenue_mismatch,
exact_duplicate_line, missing_price, invalid_status, future_order_date).
Dodano sekcje sample bad rows (1-2 wiersze per issue type) i decision
table "Silver vs Gold vs report layer" z uzasadnieniem per typ problemu.

**M2-06 — Bonus.** Sekcja "M2-06: Bonus (dla szybszych grup)", oznaczona
jako genuinely optional/skippable — dyskusja o Metric View vs materialized
aggregate + hands-on `gold.fact_sales_dashboard_segment_monthly`.

**GLOBAL-01 reuse.** Stary inline `missing = [...]` pre-check w module 2
zastapiony wywolaniem `precheck_cell(["{GOLD}.dim_date", ...,
"{GOLD}.fact_sales"], "data/generate_training_dataset.ipynb")` — pierwszy
przypadek reuse helpera poza generatorem, zgodnie z planem z Block 1.

### Weryfikacja

```
.venv/bin/python scripts/build_materials_v1.py
# -> "Built Databricks-Data-Analyst-Medi v1 materials" (bez bledow)

nbformat.read(as_version=4) + nbformat.validate(): PASS
m2_gold_kpi_best_practices.ipynb: 26 -> 36 cells (20 markdown, 16 code)
Niemagiczne komorki Python skompilowane: 15/15 OK (1 magic %run pominieta)

Walidacja WSZYSTKICH notebookow w repo (nbformat + compile): 11/11 PASS
(data/generate_training_dataset.ipynb 24, m1 20, m2 36, m3 17, m4 15,
setup x2 (4, 3), w1 exercise/solution 16/19, w2 exercise/solution 14/17)
```

Grep proof: `precheck_cell` uzyty 2x (generator + module 2), `CREATE OR
REPLACE TABLE {GOLD}.fact_sales_dashboard` obecny, KPI dictionary terms
(Revenue/Gross margin/Return rate/Orders/DQ score) obecne, reconciliation +
fan-out sekcje obecne, DQ severity/penalty_points breakdown obecny, "Bonus"
heading obecny (M2-06 + hands-on cell).

## Medi Block 3 — Workshop 1 expansion

Zakres: `docs/06-notebook-review-and-expansion-tasks.md` W1-01..W1-04,
funkcja `notebook_workshop_1(solution: bool)` w
`scripts/build_materials_v1.py` (jedna funkcja generuje exercise i solution).

**W1-01 — Pre-check.** Stary inline `missing = [...]` zastapiony wywolaniem
`precheck_cell(["{GOLD}.fact_sales_dashboard",
"{GOLD}.fact_sales_dashboard_monthly"],
"notebooks/m2_gold_kpi_best_practices.ipynb")` — drugi przypadek reuse
helpera (po module 2) poza generatorem. Dodano markdown z pelnym
prerequisite chain (00_pre_config -> generate_training_dataset -> module 2)
i jawnym komunikatem "uruchom modul 2 najpierw" jesli tabele brakuja.

**W1-02 — 5-task split.** Warsztat rozbity na dokladnie 5 ponumerowanych
zadan (Zadanie 1-5), kazde jako osobna sekcja markdown + komorki kodu:
1. zbuduj `gold.fact_sales_dashboard_channel_daily` (nowa tabela, grain
   order_date x channel — inny niz module 2's monthly/segment_monthly),
2. zdefiniuj 4 NOWE KPI nieobecne w slowniku modulu 2 (Average Order Value,
   Margin Rate %, Completed Share by Region, Revenue per Channel-Day),
3. znajdz min. 3 data-quality issues bezposrednio w
   `gold.fact_sales_dashboard` (w tym NULL po left joinie — nowy kontekst
   vs silver-level checks z modulu 2),
4. reconciliation: rollup Task 1 tabeli do (year_month, channel) vs
   `fact_sales_dashboard_monthly` rolled down do tego samego grain,
5. wypelnienie prawdziwego wiersza `docs/templates/decision-log.md` jako
   worked example (table vs view decyzja z Task 1).

**W1-03 — Expected outputs.** Kazde z 5 zadan w exercise ma sekcje
"Oczekiwany wynik (rubric)" z konkretnymi kryteriami (oczekiwane kolumny,
typy problemow, minimalne kryteria sukcesu) zamiast ogolnikowego hinta.

**W1-04 — Solution expansion.** Pelny SQL dla wszystkich 5 zadan, z
komentarzami markdown "Dlaczego" przed kazdym blokiem kodu tlumaczacymi
decyzje projektowe (np. dlaczego table a nie view, dlaczego DISTINCT order
count), plus min. 1 "Alternative considered" notatka per nietrywialne
zadanie (Zadanie 1, 3, 4) opisujaca tradeoff.

### Weryfikacja

```
.venv/bin/python scripts/build_materials_v1.py
# -> "Built Databricks-Data-Analyst-Medi v1 materials" (bez bledow)

nbformat.read(as_version=4) + nbformat.validate(): PASS na obu plikach
w1_gold_kpi_exercise.ipynb: 16 -> 19 cells, compile_errors=0 [OK]
w1_gold_kpi_solution.ipynb: 19 -> 22 cells, compile_errors=0 [OK]

Walidacja WSZYSTKICH notebookow w repo (nbformat + compile): 11/11 PASS
(data/generate_training_dataset.ipynb 24, m1 20, m2 36, m3 17, m4 15,
setup x2 (4, 3), w1 exercise/solution 16->19/19->22, w2 exercise/solution
14/17 — w2 niezmieniony, content stabilny)
```

Grep proof: `precheck_cell` uzyty w `notebook_workshop_1` (linia ~2523),
exercise zawiera 21x `TODO` i wszystkie 5 naglowkow "Zadanie 1".."Zadanie
5", solution zawiera 0x `TODO` i te same 5 naglowkow w pelni rozwiazane,
oba pliki referencja `gold.fact_sales_dashboard` (25x exercise, 35x
solution), exercise ma 5x "Oczekiwany wynik" (po jednym per zadanie),
solution zawiera filled decision-log row (data 2026-06-23, wszystkie
kolumny wypelnione, zero TODO).

Uwaga: cell-count exercise (19) jest nieznacznie powyzej dolnego targetu
14-18 z backlogu — zaakceptowano, bo kazda z 5 sekcji wymaga osobnej
markdown (zadanie + rubric) i code cell, a tresc jest genuinely nowa
(nowe KPI, nowa tabela, nowy reconciliation pair), nie relabeling
istniejacych 2-3 zadan.
