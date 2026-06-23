# Trainer Guide

Przewodnik dla prowadzącego szkolenie `Databricks-Data-Analyst-Medi`. Ten plik
zastępuje wcześniejszą wersję roboczą (rozszerzony w ramach GLOBAL-02 po
zbudowaniu wszystkich 7 bloków materiału — patrz `docs/build-log.md`).

## Format

- Czas: 7 godzin.
- Układ: 2 sesje po 3,5 godziny albo 1 dzień szkoleniowy.
- Język: polski (notebooki i komentarze SQL/Python po angielsku, zgodnie z
  konwencją branżową; markdown wyjaśniający — patrz per-moduł niżej, treść
  notebooków jest po angielsku, ten guide jest po polsku).
- Platforma: Databricks SQL Warehouse, Unity Catalog, notebooki Databricks.
- Scenariusz biznesowy: RetailHub, syntetyczny retailer, jeden ciągły
  end-to-end use case przez cały kurs (Bronze/Silver dane → Gold KPI →
  Power BI).

## Przebieg sesji

### Przed szkoleniem

1. Uruchomić `setup/00_pre_config.ipynb`.
2. Uruchomić `data/generate_training_dataset.ipynb`.
3. Zweryfikować dostęp uczestników do katalogu, schematów i SQL Warehouse.
4. Wykonać krok 0 z `docs/08-smoke-test-plan.md` (pełny dry-run) co najmniej
   raz przed pierwszym live prowadzeniem — patrz GLOBAL-03 niżej, ten test
   nie został jeszcze wykonany.
5. **Odświeżyć zrzut ekranu pricingu** — patrz sekcja "Pricing screenshot"
   niżej (GLOBAL-04). Bez tego Moduł 1 i Moduł 4 pokazują wygenerowany
   diagram zamiast realnego cennika.

### Sesja 1 (~3,5h)

1. Moduł 1: SQL Warehouse + Notebooks (45-60 min).
2. Moduł 2: Gold/KPI/best practices (90-110 min).
3. Warsztat 1: budowa analitycznego zestawu KPI w Gold (60-75 min).

### Sesja 2 (~3,5h)

1. Moduł 3: dataset i semantyka pod Power BI (90 min).
2. Warsztat 2: dataset Power BI z nastawieniem na wydajność (45-60 min).
3. Moduł 4: performance, automatyzacja i CI/CD na poziomie orientacji
   (75-90 min).

Razem: ok. 7h przy założeniu normalnego tempa z dyskusją. Jeśli grupa jest
szybka, każdy moduł i warsztat ma sekcję bonus/dyskusyjną do wydłużenia —
patrz "gdzie skracać" niżej dla kierunku odwrotnego.

## Tabela: moduł → plik → target z backlogu → faktyczna liczba komórek

Target pochodzi z `docs/06-notebook-review-and-expansion-tasks.md` sekcja 5
(per-notebook backlog). Faktyczna liczba komórek zweryfikowana lokalnie po
Block 7 (`nbformat` + cell count, patrz `docs/build-log.md`).

| Blok | Plik | Target (komórki) | Faktyczne (komórki) | Status |
|---|---|---:|---:|---|
| Foundation | `data/generate_training_dataset.ipynb` | n/a (FND-01..04) | 24 (10 md, 14 code) | rozbudowany w Block 1 |
| Moduł 1 | `notebooks/m1_sql_warehouse_notebooks.ipynb` | 18-22 | 23 | w zakresie (+1 powyżej górnej granicy, zaakceptowane) |
| Moduł 2 | `notebooks/m2_gold_kpi_best_practices.ipynb` | 24-30 | 36 | powyżej górnej granicy (zaakceptowane — bonus M2-06 + pełny reconciliation/fan-out) |
| Warsztat 1 exercise | `workshops/w1_gold_kpi_exercise.ipynb` | 14-18 | 19 | +1 powyżej (zaakceptowane, patrz build-log Block 3) |
| Warsztat 1 solution | `workshops/w1_gold_kpi_solution.ipynb` | 16-22 | 22 | w zakresie (górna granica) |
| Moduł 3 | `notebooks/m3_powerbi_semantic_dataset.ipynb` | 22-28 | 24 | w zakresie |
| Warsztat 2 exercise | `workshops/w2_powerbi_dataset_exercise.ipynb` | 12-16 | 16 | w zakresie (górna granica) |
| Warsztat 2 solution | `workshops/w2_powerbi_dataset_solution.ipynb` | 14-18 | 17 | w zakresie |
| Moduł 4 | `notebooks/m4_performance_automation_cicd_orientation.ipynb` | 20-26 | 25 | w zakresie |

Foundation nie ma jednego liczbowego targetu w backlogu (FND-01..04 to
zadania jakościowe, nie objętościowe) — 24 komórki potwierdzone jako
wystarczające w Block 1.

## Łańcuch zależności (prerequisite chain)

Udokumentowany łącznie w `docs/05-implementation-report.md` ("Rekomendowany
test live") i per-notebook w `precheck_cell()` (GLOBAL-01, helper w
`scripts/build_materials_v1.py`). Każdy notebook poniżej wymaga, by
wszystkie notebooki nad nim zostały już uruchomione w tej samej sesji
Databricks (te same katalogi/schematy):

```
setup/00_pre_config.ipynb
        |
        v
data/generate_training_dataset.ipynb   (tworzy Silver + Gold bazowe: dim_date,
        |                                dim_customer, dim_product, fact_sales,
        |                                sales_orders, order_lines, ...)
        v
notebooks/m1_sql_warehouse_notebooks.ipynb   (czyta Silver, nie wymaga Gold KPI)
        |
        v
notebooks/m2_gold_kpi_best_practices.ipynb   (buduje gold.fact_sales_dashboard,
        |                                      gold.fact_sales_dashboard_monthly,
        |                                      [bonus] _segment_monthly)
        |
        +----------------------------------+
        v                                  v
workshops/w1_gold_kpi_*.ipynb      notebooks/m3_powerbi_semantic_dataset.ipynb
(wymaga fact_sales_dashboard,      (buduje gold.v_fact_sales_incremental,
 fact_sales_dashboard_monthly       wymaga fact_sales_dashboard_monthly z m2)
 z m2; buduje WŁASNĄ tabelę                |
 fact_sales_dashboard_channel_daily)       v
                                    workshops/w2_powerbi_dataset_*.ipynb
                                    (wymaga fact_sales_dashboard_monthly z m2
                                     ORAZ v_fact_sales_incremental z m3)
                                            |
                                            v
                                    notebooks/m4_performance_automation_cicd_orientation.ipynb
                                    (czyta obiekty z m2/m3, nie tworzy nowych
                                     tabel Gold — orientacja, nie hands-on build)
```

Kluczowa pułapka dla prowadzącego: **Warsztat 2 nie zadziała po samym
Module 2** — wymaga też `gold.v_fact_sales_incremental`, który tworzy
dopiero Moduł 3. Każdy z tych notebooków ma teraz `precheck_cell()` na
początku (GLOBAL-01), więc jeśli ktoś uruchomi w złej kolejności, dostanie
czytelny błąd z nazwą brakującego obiektu i nazwą notebooka-prerequisite —
nie cichy `TABLE_OR_VIEW_NOT_FOUND` w środku zadania.

## Zakres poza v1 (scope boundary)

Z `docs/04-pre-implementation-analysis.md` sekcja "Poza zakresem v1" —
**jawnie NIE jest pokryte** w tej wersji kursu, nie wspominać jako gotowe:

- Pełne laboratorium Lakeflow Pipelines (Moduł 4 tylko orientuje w Lakeflow
  Jobs, nie buduje ani nie uruchamia żywego joba/pipeline'u).
- Pełne CI/CD z realnym deployem do dev/test/prod (`bundle/databricks.yml`
  jest referencyjny, `databricks bundle validate` jest pokazane jako
  komenda, ale notebook jawnie stwierdza, że nie była uruchomiona na żywym
  workspace).
- Pełny Power BI Desktop hands-on dla każdego uczestnika (Moduł 3 ma
  wariant "no Power BI Desktop available" — trainer-led demo lub mock
  walkthrough na screenshotach).
- AI/BI Dashboards i Genie.
- Data Vault, Inmon, data mesh.
- Pełny wariant medyczny datasetu (ten kurs używa RetailHub/retail, nie
  danych medycznych, mimo nazwy projektu "Medi" — to jest condensed/
  "miedzy"-wersja czasowa 7h, nie domena medyczna).

Jeśli uczestnik zapyta o którykolwiek z powyższych tematów — odpowiedź:
"poza zakresem tej wersji, możliwe rozszerzenie po ustabilizowaniu
podstawowej wersji", nie improwizować pełnej implementacji na żywo.

## Moduł 1 — SQL Warehouse, pricing, profiling

**Co mówić:** To jest otwarcie całego case'u RetailHub — decyzje tu
(warehouse tier, co ufać w danych, jaki jest grain) będą rewizytowane z
realnymi artefaktami w Module 2-4. Podkreślić, że celem nie jest "nauczyć
się SQL", tylko zacząć myśleć jak analytics engineer: compute, zaufanie do
danych, grain, pytania do biznesu.

**Gdzie robić demo UI:** SQL Warehouse UI na żywo — zakładki Overview, Edit,
Monitoring/Query History, Connection details (4-zakładkowy walkthrough w
notebooku). To jedyny moment kursu, gdzie warto pokazać tworzenie/edycję
warehouse'u na żywo — później moduły tylko odwołują się do tych ustawień.

**Gdzie skracać jeśli czasu mało:** Sekcja profilowania (`SHOW TABLES`,
`DESCRIBE DETAIL`, `DESCRIBE HISTORY`, min/max/nulls) można przejść szybciej
— to przygotowanie do Module 2, nie nowa koncepcja. Mini-quiz na końcu
(M1-04) można zrobić jako szybkie pytanie do grupy zamiast pisanej
dyskusji, jeśli czasu mało.

**Typowe błędy uczestników:** Mylenie Serverless/Pro/Classic jako "to samo
tylko inna nazwa" — podkreślić różnicę w cold start i modelu kosztowym.
Próba odpowiedzi na Step 3 (3 pytania do biznesu) jako pytania techniczne
zamiast biznesowych — naprowadzić na pytania o definicje (np. "czy Returned
liczy się jako ujemny revenue").

## Moduł 2 — Medallion, Gold, Kimball, KPI

**Co mówić:** To jest rdzeń merytoryczny kursu (najdłuższy moduł, 90-110
min). Kluczowy przekaz: grain deklarujemy PRZED budową tabeli, nie po
fakcie. Gold to nie "kolejna kopia danych" — to kontrakt z konsumentem
(BI/Power BI), z jawnym ownership i quality bar wyższym niż Silver.

**Gdzie robić demo UI:** Catalog Explorer — pokazać hierarchię
katalog/schema/tabela i lineage (`source_catalog_explorer_hierarchy.png`,
`source_catalog_explorer_lineage.png` jako fallback jeśli nie ma dostępu do
żywego workspace'u z danymi lineage). DESCRIBE TABLE na `gold.fact_sales` i
`gold.dim_date` najlepiej pokazać live w SQL Editor, nie tylko jako wynik w
notebooku.

**Gdzie skracać jeśli czasu mało:** M2-06 (bonus: Metric View vs
materialized aggregate, `fact_sales_dashboard_segment_monthly`) jest
explicit oznaczony jako "dla szybszych grup" — pierwszy kandydat do
pominięcia. Drugi kandydat: skrócić deliberate fan-out join demo (M2-04) do
pokazania wyniku zamiast budowania go krok po kroku na żywo.

**Typowe błędy uczestników:** `COUNT(*)` zamiast `COUNT(DISTINCT order_id)`
przy liczeniu zamówień na grain order-line (zawyżony wynik) — to jest
celowo zaszyte jako pułapka w M2-04, naprowadzić pytaniem "ile wierszy ma
jedno zamówienie z 3 produktami?". Mylenie `gold.fact_sales` (generator,
order-line grain, do walidacji) z `gold.fact_sales_dashboard`
(denormalizowany, dashboard-ready) — to są DWA różne obiekty Gold, nie
synonimy.

## Warsztat 1 — Gold KPI package

**Co mówić:** To jest pierwszy w pełni samodzielny blok pracy uczestnika.
5 zadań, każde z jawnym "Oczekiwany wynik (rubric)" w exercise — czytać
rubric NA GŁOS przed puszczeniem grupy do pracy, żeby uczestnicy wiedzieli,
kiedy są "gotowi" z zadaniem.

**Gdzie robić demo UI:** Brak nowego UI w tym warsztacie — to jest praca w
notebooku/SQL. Jeśli ktoś utknie, pokazać Query History, żeby zobaczyć,
czy zapytanie w ogóle się wykonało.

**Gdzie skracać jeśli czasu mało:** Zadanie 5 (decision log) jest
najszybsze do pominięcia/skrócenia do ustnej dyskusji zamiast pisanego
wpisu — wartość edukacyjna jest w Zadaniach 1-4. Jeśli naprawdę mało czasu,
można zrobić Zadania 1-3 jako grupę, 4-5 jako trener-prowadzony walkthrough
solution.

**Typowe błędy uczestników:** Zadanie 1 (nowa tabela
`fact_sales_dashboard_channel_daily`) — uczestnicy czasem kopiują grain z
Module 2 (monthly) zamiast budować nowy grain (`order_date x channel`).
Zadanie 3 (data quality) — uczestnicy szukają tylko NULL-i, pomijają NULL
powstały PO left joinie (nowy kontekst vs Silver-level checks z Module 2).

## Moduł 3 — Power BI semantic dataset

**Co mówić:** Centralna decyzja modułu: Import vs DirectQuery to nie
wybór "lepszy/gorszy", tylko tradeoff freshness vs koszt/responsywność.
Podkreślić query fan-out: koszt DirectQuery skaluje się jako
`visuals x filter changes x concurrent users`, nie liniowo z wolumenem
danych.

**Gdzie robić demo UI:** To jest moduł z największą zależnością od
dostępności Power BI Desktop. Jeśli dostępny: live connection walkthrough
(8 kroków, server hostname/HTTP path z SQL Warehouse → Connection details).
Jeśli NIEDOSTĘPNY dla wszystkich uczestników: użyć wariantu "no Power BI
Desktop available" w notebooku — trainer-led demo na jednej maszynie LUB
mock-narrated-walkthrough na istniejących screenshotach
(`source_powerbi_directquery_connector.webp`,
`powerbi_connection_walkthrough.png`) + SQL-owe komórki w tym samym
notebooku jako "real data without Power BI UI".

**Gdzie skracać jeśli czasu mało:** Sekcja "mock report walkthrough"
(M3-05, widget-by-widget na `powerbi_report_mockup.png`) można skrócić do
2-3 reprezentatywnych widgetów zamiast wszystkich 5+drill-through, jeśli
grupa już rozumie zasadę "jeden mark per month/region → aggregate,
drill-through → detail".

**Typowe błędy uczestników:** Założenie, że incremental refresh
(RangeStart/RangeEnd) to to samo co WHERE z literałem daty — podkreślić
half-open interval i to, że Power BI Service podstawia te parametry
automatycznie. Boundary-check (`order_date = RangeEnd` musi zwrócić 0
wierszy) to częsty "aha moment" — nie pomijać tej komórki.

## Warsztat 2 — Power BI dataset readiness

**Co mówić:** To jest aplikacja decyzji z Module 3 do KONKRETNEGO datasetu
(nie ogólna odpowiedź). Kluczowy cytat z solution do podkreślenia na głos:
"Import is the baseline... DirectQuery is reserved as the exception" —
zgodne z Ryzykiem 3 z `docs/04-pre-implementation-analysis.md`.

**Gdzie robić demo UI:** Jak w Warsztacie 1 — głównie praca w
notebooku/SQL, bez nowego UI poza tym, co już pokazano w Module 3.

**Gdzie skracać jeśli czasu mało:** Zadanie 6 (cost guardrails wg
`docs/templates/cost-awareness-checklist.md`) jest najszybsze do skrócenia
do ustnej dyskusji — wartość edukacyjna jest w Zadaniach 1-5 (wybór source,
Import/DirectQuery decyzja, incremental refresh, BI contract).

**Typowe błędy uczestników:** Zadanie 4 (własny boundary test na innym
oknie dat niż przykład z Module 3) — uczestnicy czasem kopiują dokładnie
przykład z Module 3 zamiast użyć nowego okna (`2025-04-01`/`2025-07-01`).
Zadanie 3 — uczestnicy czasem wybierają DirectQuery dla summary page
"bo jest dokładniejszy", mimo że summary page ma miesięczny grain i nie
potrzebuje intra-day freshness.

## Moduł 4 — Performance, automation, CI/CD orientation

**Co mówić:** To jest moduł zamykający — pokazuje konsekwencje decyzji z
Module 2/3 (Gold vs Silver, filtr daty, DirectQuery) w postaci realnych
liczb (EXPLAIN FORMATTED, rows scanned). CI/CD i Lakeflow Jobs są
orientacyjne, nie hands-on — jawnie powiedzieć grupie, że nie będą sami
wdrażać joba na żywym workspace w tym kursie.

**Gdzie robić demo UI:** Query Profile UI (jeśli dostępny live workspace) —
pokazać realny query plan z Query History, nie tylko EXPLAIN FORMATTED w
notebooku. Jeśli nie ma czasu/dostępu, tabela "scan size, shuffle, joins,
czas" + krok-po-kroku jak powiązać Power BI Performance Analyzer z Query
History wystarczy jako narracja.

**Gdzie skracać jeśli czasu mało:** Trzecia para porównawcza (M4-01c,
`SELECT *` vs wybrane kolumny) jest najmniej krytyczna z trzech par —
pierwsze dwie (Silver detail vs Gold aggregate; filtr daty vs bez) niosą
więcej nowej treści. Sekcja DABs/`bundle/databricks.yml` (M4-05) — pokazać
plik, nie odtwarzać całego `databricks bundle validate` na żywo, jeśli nie
ma pewności co do środowiska CLI.

**Typowe błędy uczestników:** Mylenie Lakeflow Jobs z Lakeflow Pipelines —
podkreślić explicit sekcję "Jobs vs Lakeflow Pipelines" w notebooku.
Założenie, że `bundle/databricks.yml` był testowany na żywym workspace —
notebook i ten guide jawnie stwierdzają, że NIE był (referencyjny, walidacja
składni YAML lokalnie tak, deploy nie).

## Pricing screenshot — działanie wymagane przed pierwszym szkoleniem

`assets/images/sql_warehouse_cost_decision.png` to wygenerowany diagram
(whiteboard/sketch style), NIE jest realnym zrzutem ekranu z Databricks
Pricing. Moduł 1 i Moduł 4 mają teraz jawną notatkę TODO w markdown przy
tym obrazie (dodane w Block 8 / GLOBAL-04):

> Ten zrzut ekranu trzeba odświeżyć z aktualnej strony Databricks Pricing
> przed pierwszym prowadzeniem szkolenia — obecny diagram jest
> wygenerowany, nie jest realnym cennikiem.

Akcja dla trenera/właściciela kursu przed pierwszym live prowadzeniem:
zrobić realny zrzut ekranu z oficjalnej strony Databricks Pricing, zapisać
jako `assets/images/databricks_pricing_YYYY-MM-DD.png` (z aktualną datą),
opcjonalnie podmienić referencję w notebookach Moduł 1/4 albo dołączyć
obok istniejącego diagramu.

## Runtime smoke test

Pełny plan w `docs/08-smoke-test-plan.md` (GLOBAL-03). **Nie został jeszcze
wykonany** na żywym Databricks workspace — to jest następny krok przed
pierwszym live prowadzeniem, nie coś już potwierdzonego.
