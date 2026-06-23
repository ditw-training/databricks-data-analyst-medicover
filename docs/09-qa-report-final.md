# Final QA Report — Block 9 (Faza 3)

Status: weryfikacja końcowa wykonana ze świeżym kontekstem (agent nie
uczestniczył w budowie Bloków 1-8). Zakres: pełny sweep repo —
11 notebookow, generator, dokumentacja, `bundle/databricks.yml`, assety.

Metoda: statyczna analiza (inwentaryzacja `CREATE TABLE`/`CREATE VIEW` i
wszystkich referencji `FROM`/`JOIN` po wszystkich 11 notebookach, grep po
`precheck_cell`, `nbformat.validate` + `ast.parse` po wszystkich komórkach
kodu, `yaml.safe_load` na bundle, porównanie cell countów z
`docs/TRAINER_GUIDE.md`). Żaden notebook nie był uruchamiany na żywym
Databricks workspace — to pozostaje zadaniem `docs/08-smoke-test-plan.md`.

## 1. Registry consistency — [OK]

Zbudowano pełną inwentaryzację obiektów Silver/Gold:

**Silver (generator, `saveAsTable`):** `customers`, `products`,
`sales_orders`, `order_lines` — schematy wyciągnięte bezpośrednio z kodu
PySpark (nie z `CREATE TABLE`, bo to zapis DataFrame).

**Gold (CREATE OR REPLACE TABLE/VIEW), w kolejności tworzenia:**

| Obiekt | Tworzony w | Typ |
|---|---|---|
| `gold.dim_date`, `gold.dim_product`, `gold.dim_customer`, `gold.fact_sales`, `gold.kpi_daily`, `gold.revenue_monthly` | `data/generate_training_dataset.ipynb` | TABLE |
| `gold.fact_sales_dashboard`, `gold.fact_sales_dashboard_monthly` | Moduł 2 | TABLE |
| `gold.data_quality_score` | Moduł 2 (DQ scorecard, nie BI-facing) | TABLE |
| `gold.fact_sales_dashboard_segment_monthly` | Moduł 2 (M2-06, bonus) | TABLE |
| `gold.fact_sales_dashboard_channel_daily` | Warsztat 1 | TABLE |
| `gold.v_fact_sales_incremental` | Moduł 3 | VIEW |

Skrzyżowano każdą referencję `FROM`/`JOIN` (regex sweep po wszystkich
komórkach kodu we wszystkich 11 plikach) z tą listą — **zero orphan
references**. Każda tabela/widok użyty w SELECT/JOIN jest utworzony gdzieś
wcześniej w łańcuchu zależności.

Zweryfikowano też kolumny (nie tylko nazwy obiektów) dla wszystkich
nietrywialnych CTAS i JOIN-ów:
- `silver.order_lines` ma `customer_id` (poprzedni bug z Block 1, fixed)
  potwierdzony jako nadal naprawiony — `customer_id` obecny w schemacie.
- `gold.fact_sales_dashboard` ma `unit_price`/`unit_cost`/`discount_pct`
  (poprzedni bug z Block 1) — nadal obecne.
- `gold.fact_sales_dashboard_monthly` ma `channel` w SELECT/GROUP BY — co
  jest wymagane przez Warsztat 1 Zadanie 4 (join po `channel` między
  `fact_sales_dashboard_channel_daily` a `_monthly`) — kolumna istnieje,
  join jest poprawny.
- `gold.v_fact_sales_incremental` SELECT-uje tylko kolumny faktycznie
  obecne w `fact_sales_dashboard` (`segment`, `customer_region`,
  `subcategory` itd.) — zgodne.

Nie znaleziono żadnego nowego wystąpienia bug-class z
`docs/06-notebook-review-and-expansion-tasks.md` sekcja 1 (kolumna
referencjonowana, której nie ma w źródle).

## 2. Pre-check (`precheck_cell`) coverage i poprawność — [OK]

7 wywołań `precheck_cell` w `scripts/build_materials_v1.py`, każde
zweryfikowane osobno (linia w generatorze, notebook docelowy, lista tabel,
nazwa prerequisite-notebooka):

| Notebook | Wymagane tabele | Prereq notebook w komunikacie | Status |
|---|---|---|---|
| `data/generate_training_dataset.ipynb` | 6 obiektów Gold | siebie samego (self-check) | OK |
| `notebooks/m1_sql_warehouse_notebooks.ipynb` | 4 Silver + `fact_sales` | `data/generate_training_dataset.ipynb` | OK |
| `notebooks/m2_gold_kpi_best_practices.ipynb` | 4 obiekty Gold (dim×3 + fact_sales) | `data/generate_training_dataset.ipynb` | OK |
| `notebooks/m3_powerbi_semantic_dataset.ipynb` | `fact_sales_dashboard`, `_monthly` | `notebooks/m2_gold_kpi_best_practices.ipynb` | OK (poprawna nazwa pliku) |
| `notebooks/m4_performance_automation_cicd_orientation.ipynb` | `fact_sales_dashboard`, `_monthly`, `v_fact_sales_incremental` | `notebooks/m3_powerbi_semantic_dataset.ipynb` | patrz uwaga niżej |
| `workshops/w1_gold_kpi_*.ipynb` | `fact_sales_dashboard`, `_monthly` | `notebooks/m2_gold_kpi_best_practices.ipynb` | OK |
| `workshops/w2_powerbi_dataset_*.ipynb` | `fact_sales_dashboard_monthly`, `v_fact_sales_incremental` | oba: `m2_gold_kpi_best_practices.ipynb` (dla monthly) i `m3_powerbi_semantic_dataset.ipynb` (dla incremental) | OK |

Nie znaleziono ponownego wystąpienia bug-class "zła nazwa pliku
prerequisite" z Block 7 (Warsztat 2 fix). `grep -l "m2_gold_dashboard"` na
całym repo zwraca tylko historyczne wzmianki w `docs/build-log.md`
(opisujące sam fix), zero w aktywnym kodzie/notebookach.

**[MINOR]** Moduł 4 wymaga 3 tabel z dwóch różnych modułów
(`fact_sales_dashboard`/`_monthly` z Modułu 2, `v_fact_sales_incremental` z
Modułu 3), ale `prereq_notebook` w komunikacie błędu wskazuje tylko
`m3_powerbi_semantic_dataset.ipynb`. Helper `precheck_cell()` ma jeden
string `prereq_notebook` dla całej listy tabel (z założenia — patrz
docstring), więc to nie jest "zła nazwa", tylko niepełna w hipotetycznym
scenariuszu, gdyby ktoś pominął zarówno Moduł 2 jak i Moduł 3 i odpalił
Moduł 4 bezpośrednio. W praktyce ryzyko jest niskie: zalecana kolejność w
`docs/TRAINER_GUIDE.md`/`docs/08-smoke-test-plan.md` jest ściśle
sekwencyjna (m1→m2→{w1,m3}→w2→m4), a precheck Modułu 3 i tak złapie brak
Modułu 2, zanim ktokolwiek dotrze do Modułu 4. Nie naprawiono (wymagałoby
rozszerzenia `precheck_cell()` o per-tabelę prereq mapping — większa zmiana
designu helpera używanego w 7 miejscach), udokumentowane tutaj.

Workshop 2's precheck dla `v_fact_sales_incremental` POPRAWNIE wskazuje
`m3_powerbi_semantic_dataset.ipynb` jako osobny prereq message component
(ten przypadek jest już granularny — dwa różne required_tables grupy z
opisowym połączonym stringiem) — różni się od Modułu 4 tym, że W2's
`prereq_notebook` string explicite wymienia oba pliki z dopiskiem "(for
X)/(for Y)", podczas gdy M4 ma tylko jeden plik wymieniony mimo 3 tabel z 2
źródeł. Nie blokujące, ale asymetria w jakości komunikatu między tymi
dwoma notebookami.

## 3. TODO/solution discipline — [OK]

```
workshops/w1_gold_kpi_exercise.ipynb:  15 wystąpień "TODO"
workshops/w1_gold_kpi_solution.ipynb:   0 wystąpień "TODO"
workshops/w2_powerbi_dataset_exercise.ipynb: 11 wystąpień "TODO"
workshops/w2_powerbi_dataset_solution.ipynb:  0 wystąpień "TODO"
```

Oba pliki `_solution.ipynb` mają zero TODO i pełny, rozwiązany SQL/Python
dla wszystkich zadań (5 dla W1, 6 dla W2). Oba pliki `_exercise.ipynb` mają
TODO rozłożone po wszystkich zadaniach.

## 4. Terminology/naming consistency — [MINOR, naprawione częściowo]

Nazwy tabel/widoków: **zero literówek** w całym repo (sprawdzono pod kątem
`fact_sales_dashbord`, `fact_sale_dashboard`, `fact_sales_dahsboard` i
podobnych — zero trafień). Pełna lista 16 unikalnych nazw obiektów
`{GOLD}.*`/`{SILVER}.*` użytych w repo jest spójna wszędzie.

**[BLOCKER, udokumentowane, nie naprawione w kodzie]** Notebooki (treść
markdown + komentarze kodu) są w **całości po angielsku** w wszystkich 11
plikach `.ipynb`, mimo że `docs/01-training-structure.md` (Etap "wymagania
wlasciciela"/"Zasady budowy", linia 77) jawnie stwierdza: "Materialy w
notebookach po polsku". Ten wymóg nigdy nie został zrealizowany — był
łamany od pierwszego buildu (`implementacja v1`) przez wszystkie 8 bloków
rozbudowy. Dowód ilościowy (markery polskich znaków diakrytycznych +
typowych polskich słów funkcyjnych w komórkach markdown):

```
m2_gold_kpi_best_practices.ipynb:    polish_markers=0   english_markers=147
m3_powerbi_semantic_dataset.ipynb:   polish_markers=0   english_markers=141
w2_powerbi_dataset_exercise.ipynb:   polish_markers=0   english_markers=46
m1_sql_warehouse_notebooks.ipynb:    polish_markers=3   english_markers=147
w1_gold_kpi_exercise.ipynb:          polish_markers=11  english_markers=73
```

Block 8 udokumentował tę sytuację retroaktywnie w
`docs/TRAINER_GUIDE.md` ("Format" sekcja): *"Język: polski (notebooki i
komentarze SQL/Python po angielsku, zgodnie z konwencją branżową... treść
notebooków jest po angielsku, ten guide jest po polsku)"* — czyli decyzja
projektowa **została po cichu zmieniona w trakcie budowy** i nigdy nie
zsynchronizowana wstecz z `docs/01-training-structure.md`, które nadal
mówiło co innego. To nie jest literówka ani drobny przeoczony fragment —
to retroaktywna zmiana zakresu o bardzo dużej skali (cała treść
edukacyjna kursu), zaakceptowana implicite przez kolejne 7 bloków
rozbudowy bez jawnej decyzji właściciela materiałów. Oznaczam jako
**[BLOCKER do decyzji właściciela]**, nie naprawiam (tłumaczenie ~4700
linii markdown na polski w ramach tej sesji QA byłoby zgadywaniem dużej
decyzji projektowej, niezgodnym z zakresem tego zadania). **Naprawione w
tym bloku:** doklejono jawną adnotację do `docs/01-training-structure.md`
(linia 77 obszar), wskazującą faktyczny stan i odsyłającą do
`docs/TRAINER_GUIDE.md` jako źródła prawdy — żeby dokumentacja planistyczna
nie kłamała wprost.

**[MINOR, naprawione]** Niespójność nazewnictwa zadań między warsztatami:
Warsztat 1 nagłówki to "Zadanie 1".."Zadanie 5" (polski), Warsztat 2
nagłówki to "Task 1".."Task 6" (angielski) — to samo pojęcie nazwane
inaczej w dwóch siostrzanych dokumentach. Każdy notebook jest *wewnętrznie*
spójny (W1 zawsze "Zadanie", W2 zawsze "Task"), ale `docs/TRAINER_GUIDE.md`
i `docs/08-smoke-test-plan.md` w sekcjach dot. Warsztatu 2 błędnie używały
"Zadanie N" zamiast "Task N" (kopiowanie konwencji z sekcji Warsztatu 1).
Naprawiono bezpośrednio w dokumentacji (`docs/TRAINER_GUIDE.md` linie
~259-267, `docs/08-smoke-test-plan.md` linia ~156-157) — zamieniono
"Zadanie"/"Zadania" na "Task"/"Tasks" tam, gdzie odnoszą się do Warsztatu
2. Nie zmieniano samych notebooków (nagłówki "Task N" w W2 są poprawne,
zgodne z resztą treści notebooka po angielsku — patrz finding wyżej).

## 5. Image references — [OK]

22 unikalne ścieżki obrazów referencjonowane w markdown komórkach (21
rzeczywistych plików + 1 wzmianka tekstowa, nie tag obrazu:
`databricks_pricing_YYYY-MM-DD.png`, intencjonalny placeholder dla trenera
opisany w GLOBAL-04/Block 8). Wszystkie 21 plików na dysku w
`assets/images/` (poza `.gitkeep`) są referencjonowane przynajmniej raz —
**zero orphaned assets**. `docs/07-visual-materials-map.md` dokładnie
odzwierciedla aktualny stan (4 source screenshoty + 17 whiteboard
visuals = 21).

## 6. `bundle/databricks.yml` validity — [BLOCKER, naprawione]

`yaml.safe_load()` — plik jest poprawnym YAML (bez regresji od Block 6).

**Znaleziony i naprawiony bug:** task `build_bi_dataset` wskazywał na
`m3_powerbi_semantic_dataset.ipynb` (notebook, który faktycznie buduje
`gold.v_fact_sales_incremental`), a task `refresh_incremental_view`
wskazywał na `m4_performance_automation_cicd_orientation.ipynb` — notebook,
który **nie tworzy żadnej tabeli Gold** (potwierdzone osobnym sweep'em:
zero `CREATE TABLE`/`CREATE VIEW` w `m4_*`, i jawnie potwierdzone przez
`docs/TRAINER_GUIDE.md`: "czyta obiekty z m2/m3, nie tworzy nowych tabel
Gold — orientacja, nie hands-on build"). Nazwy tasków były więc zamienione
względem tego, co faktycznie robi notebook pod każdym z nich.

Naprawiono w `scripts/build_materials_v1.py` (`write_bundle()`): task
wskazujący na `m3_powerbi_semantic_dataset.ipynb` przemianowano na
`refresh_incremental_view` (zgodne z tym, co ten notebook faktycznie
robi), a task wskazujący na `m4_*.ipynb` przemianowano na
`validate_bi_readiness` (zgodne z jego orientacyjną, read-only naturą).
Zregenerowano i zweryfikowano:

```
Job refresh_gold_bi_dataset: 4 tasks
  - validate_sources -> ../notebooks/m1_sql_warehouse_notebooks.ipynb
  - refresh_gold -> ../notebooks/m2_gold_kpi_best_practices.ipynb
  - refresh_incremental_view -> ../notebooks/m3_powerbi_semantic_dataset.ipynb
  - validate_bi_readiness -> ../notebooks/m4_performance_automation_cicd_orientation.ipynb
```

`git diff` na `bundle/databricks.yml` potwierdza dokładnie tę zamianę (6
linii zmienionych, bez innych regresji — `targets`, `variables`,
`trigger.periodic` niezmienione).

## 7. Cell-count vs backlog targets — [OK]

Świeży przebieg `len(json.load(open(PATH))['cells'])` po regeneracji,
porównany z tabelą w `docs/TRAINER_GUIDE.md`:

| Plik | TRAINER_GUIDE.md | Faktyczne (świeży sweep) | Zgodność |
|---|---:|---:|---|
| `data/generate_training_dataset.ipynb` | 24 | 24 | OK |
| `notebooks/m1_sql_warehouse_notebooks.ipynb` | 23 | 23 | OK |
| `notebooks/m2_gold_kpi_best_practices.ipynb` | 36 | 36 | OK |
| `workshops/w1_gold_kpi_exercise.ipynb` | 19 | 19 | OK |
| `workshops/w1_gold_kpi_solution.ipynb` | 22 | 22 | OK |
| `notebooks/m3_powerbi_semantic_dataset.ipynb` | 24 | 24 | OK |
| `workshops/w2_powerbi_dataset_exercise.ipynb` | 16 | 16 | OK |
| `workshops/w2_powerbi_dataset_solution.ipynb` | 17 | 17 | OK |
| `notebooks/m4_performance_automation_cicd_orientation.ipynb` | 25 | 25 | OK |

Tabela jest aktualna, nie jest stale sprzed Block 8. `setup/00_pre_config`
(4 komórki) i `setup/00_setup` (3 komórki) nie mają wiersza w tabeli (poza
zakresem backlogu — FND nie ma numerycznego targetu, zgodnie z notatką pod
tabelą), zgodne ze stanem repo.

## 8. Full notebook validity — [OK]

Świeży sweep, niezależny od poprzednich blokowych weryfikacji:

```
nbformat.read(as_version=4) + nbformat.validate(): PASS na wszystkich 11 plikach
ast.parse() na każdej niemagicznej komórce kodu: 0 błędów kompilacji
  data/generate_training_dataset.ipynb: cells=24, code=14, magics=1, errors=0
  notebooks/m1_sql_warehouse_notebooks.ipynb: cells=23, code=10, magics=1, errors=0
  notebooks/m2_gold_kpi_best_practices.ipynb: cells=36, code=16, magics=1, errors=0
  notebooks/m3_powerbi_semantic_dataset.ipynb: cells=24, code=7, magics=1, errors=0
  notebooks/m4_performance_automation_cicd_orientation.ipynb: cells=25, code=12, magics=1, errors=0
  setup/00_pre_config.ipynb: cells=4, code=2, magics=0, errors=0
  setup/00_setup.ipynb: cells=3, code=2, magics=0, errors=0
  workshops/w1_gold_kpi_exercise.ipynb: cells=19, code=9, magics=1, errors=0
  workshops/w1_gold_kpi_solution.ipynb: cells=22, code=10, magics=1, errors=0
  workshops/w2_powerbi_dataset_exercise.ipynb: cells=16, code=5, magics=1, errors=0
  workshops/w2_powerbi_dataset_solution.ipynb: cells=17, code=6, magics=1, errors=0
TOTAL COMPILE ERRORS: 0
```

Po naprawie bundle.yml zregenerowano cały projekt
(`.venv/bin/python scripts/build_materials_v1.py`) i powtórzono powyższy
sweep — wynik identyczny, zero regresji. `git diff` na wszystkich 11
plikach `.ipynb` po regeneracji pokazuje **zero linii różnicy poza
`"id"`** (losowy UUID komórki per build run) — czyli regeneracja po
naprawie bundle.yml nie zmieniła żadnej treści notebooków.

## 9. Smoke test plan accuracy — [OK]

`docs/08-smoke-test-plan.md` porównany ze świeżym `find . -name "*.ipynb"`:
lista 11 plików w sekcji "0. Stan repo" zgadza się dokładnie z aktualnym
stanem repo (te same 11 ścieżek, ten sam porządek). Run order (8 kroków,
sekcja 2) zgodny z łańcuchem zależności potwierdzonym przez
`precheck_cell` wywołania (check 2 wyżej). Tabela 5 obiektów BI Gold
(sekcja 3.4) zgodna z rejestrem zbudowanym w check 1 wyżej — wszystkie 5
obiektów (`fact_sales_dashboard`, `_monthly`, `_segment_monthly` [bonus],
`fact_sales_dashboard_channel_daily`, `v_fact_sales_incremental`) faktycznie
istnieją w kodzie z poprawnym "tworzony w" przypisaniem do modułu/warsztatu.
Naprawiono drobną niespójność terminologii Task/Zadanie w sekcji 3.5 (patrz
check 4).

## Podsumowanie

| # | Check | Werdykt |
|---|---|---|
| 1 | Registry consistency | OK |
| 2 | Pre-check coverage i poprawność | OK (1 MINOR udokumentowany, nie naprawiony) |
| 3 | TODO/solution discipline | OK |
| 4 | Terminology/naming consistency | 1 BLOCKER udokumentowany (język notebooków, nie naprawiony — decyzja właściciela), 1 MINOR naprawiony (Task/Zadanie w docs) |
| 5 | Image references | OK |
| 6 | `bundle/databricks.yml` validity | BLOCKER znaleziony i naprawiony (zamienione task_key/notebook_path) |
| 7 | Cell-count vs TRAINER_GUIDE.md | OK |
| 8 | Full notebook validity (11/11) | OK, 0 błędów kompilacji |
| 9 | Smoke test plan accuracy | OK (drobna korekta terminologii) |

## Werdykt ogólny

**Materiał jest gotowy do live smoke testu** (`docs/08-smoke-test-plan.md`)
**z jednym zastrzeżeniem do decyzji właściciela przed pierwszym
prowadzeniem na żywo**: treść notebooków jest po angielsku, nie po polsku,
wbrew pierwotnemu wymogowi z `docs/01-training-structure.md`. To nie
blokuje technicznej poprawności (rejestr obiektów, pre-checki, walidacja
notebooków, bundle DABs — wszystko OK lub naprawione), ale jest realną
rozbieżnością ze sformułowanym wymogiem projektu, którą właściciel
materiałów powinien świadomie zaakceptować (tak jak częściowo już zrobił w
`docs/TRAINER_GUIDE.md`) albo zlecić tłumaczenie przed pierwszą sesją.

Żaden ze znalezionych problemów technicznych (bundle.yml task wiring) nie
wymagał decyzji projektowej — naprawiono bezpośrednio przez generator,
zregenerowano, zweryfikowano zero regresji.

## Naprawione w tym bloku

1. `scripts/build_materials_v1.py` (`write_bundle()`): zamieniono
   `task_key`/`notebook_path` pary tak, by `refresh_incremental_view`
   wskazywał na `m3_powerbi_semantic_dataset.ipynb` (faktyczny twórca
   `v_fact_sales_incremental`), a nowy `validate_bi_readiness` wskazywał na
   `m4_performance_automation_cicd_orientation.ipynb` (orientacja,
   zero nowych tabel).
2. `docs/01-training-structure.md`: dodano jawną adnotację przy regule
   "Materialy w notebookach po polsku", wskazującą faktyczny stan
   (notebooki po angielsku) i odsyłającą do `docs/TRAINER_GUIDE.md`.
3. `docs/TRAINER_GUIDE.md`: poprawiono "Zadanie N" → "Task N" w sekcji
   Warsztatu 2 (linie ~259-267), zgodnie z faktycznymi nagłówkami w
   `workshops/w2_*.ipynb`.
4. `docs/08-smoke-test-plan.md`: poprawiono "Zadanie 5/6" → "Task 5/6" w
   sekcji 3.5 (Workshopy), z tego samego powodu.

## Nie naprawione, udokumentowane (wymaga decyzji właściciela)

1. **Język notebooków** (check 4) — cała treść markdown/komentarzy w 11
   notebookach jest po angielsku, wbrew pierwotnemu wymogowi "po polsku" z
   `docs/01-training-structure.md`. Tłumaczenie ~4700 linii treści to
   osobny, świadomy projekt, nie coś do zgadnięcia w ramach QA.
2. **Moduł 4 precheck message granularity** (check 2) — komunikat błędu
   wskazuje tylko `m3_*.ipynb` jako prereq mimo że 3 wymagane tabele
   pochodzą z 2 różnych modułów (M2 i M3). Niskie ryzyko praktyczne
   (sekwencyjny run order + precheck M3 łapie brak M2 wcześniej), ale
   wymagałoby rozszerzenia signature `precheck_cell()` (per-tabela prereq
   mapping) używanego w 7 miejscach — większa zmiana niż "cheap fix".
