# Runtime smoke test plan

Status: **plan, nie wynik**. Ten dokument opisuje dokładną kolejność
uruchamiania notebooków na żywym Databricks workspace oraz checklistę do
zweryfikowania na każdym kroku. Test **nie został jeszcze wykonany** — to
jest następny human-driven krok przed pierwszym live prowadzeniem szkolenia
`Databricks-Data-Analyst-Medi`. Wszystko, co dotychczas zweryfikowano (patrz
`docs/build-log.md`, Block 1-7), to walidacja statyczna: `nbformat.validate`
i `ast.parse`/`py_compile` na komórkach Python. Żaden notebook nie był
uruchomiony na żywym klastrze/SQL Warehouse.

Bazuje na `docs/05-implementation-report.md` sekcja "Rekomendowany test
live", zaktualizowane i rozszerzone o stan repo po 7 blokach rozbudowy
(GLOBAL-03, `docs/06-notebook-review-and-expansion-tasks.md`).

## 0. Stan repo — potwierdzenie listy plików

Lista notebooków potwierdzona poleceniem `find . -name "*.ipynb"` w trakcie
budowy tego planu (Block 8):

```
data/generate_training_dataset.ipynb
notebooks/m1_sql_warehouse_notebooks.ipynb
notebooks/m2_gold_kpi_best_practices.ipynb
notebooks/m3_powerbi_semantic_dataset.ipynb
notebooks/m4_performance_automation_cicd_orientation.ipynb
setup/00_pre_config.ipynb
setup/00_setup.ipynb
workshops/w1_gold_kpi_exercise.ipynb
workshops/w1_gold_kpi_solution.ipynb
workshops/w2_powerbi_dataset_exercise.ipynb
workshops/w2_powerbi_dataset_solution.ipynb
```

11 plików — zgodne z listą artefaktów z `docs/05-implementation-report.md`
(żaden notebook nie został dodany ani usunięty od czasu tego raportu;
zmieniła się tylko zawartość/objętość komórek w blokach 1-7).

## 1. Przygotowanie środowiska

1. Zaimportować cały folder `Databricks-Data-Analyst-Medi` do Databricks
   Workspace (Repos lub import workspace files).
2. Potwierdzić dostęp do Unity Catalog z uprawnieniami do tworzenia
   katalogu/schematów (albo użyć już istniejącego sandbox catalogu —
   zależnie od konfiguracji w `setup/00_pre_config.ipynb`).
3. Potwierdzić, że jest aktywny klaster (do notebooków Python/SQL z
   `%run`) ORAZ SQL Warehouse (do Module 1 UI walkthrough i Power BI
   connection w Module 3).

## 2. Kolejność uruchamiania (run order)

Uruchamiać DOKŁADNIE w tej kolejności — każdy krok zależy od obiektów
utworzonych w poprzednich (pełny graf zależności w
`docs/TRAINER_GUIDE.md` sekcja "Łańcuch zależności"):

| # | Notebook | Tworzy/wymaga |
|---|---|---|
| 1 | `setup/00_pre_config.ipynb` | tworzy katalog/schematy (Bronze/Silver/Gold) |
| 2 | `data/generate_training_dataset.ipynb` | tworzy 4 tabele Silver + 6 obiektów Gold bazowych (w tym `gold.fact_sales`, `gold.dim_date`, `gold.dim_customer`, `gold.dim_product`); kończy się własnym `precheck_cell`/assert self-checkiem |
| 3 | `notebooks/m1_sql_warehouse_notebooks.ipynb` | tylko czyta Silver; nie tworzy nowych tabel trwałych |
| 4 | `notebooks/m2_gold_kpi_best_practices.ipynb` | tworzy `gold.fact_sales_dashboard`, `gold.fact_sales_dashboard_monthly`, [bonus, opcjonalnie] `gold.fact_sales_dashboard_segment_monthly` |
| 5 | `workshops/w1_gold_kpi_solution.ipynb` | tworzy `gold.fact_sales_dashboard_channel_daily`; wymaga obiektów z kroku 4 |
| 6 | `notebooks/m3_powerbi_semantic_dataset.ipynb` | tworzy `gold.v_fact_sales_incremental`; wymaga `fact_sales_dashboard_monthly` z kroku 4 |
| 7 | `workshops/w2_powerbi_dataset_solution.ipynb` | nie tworzy nowych trwałych tabel (czyta i waliduje); wymaga obiektów z kroków 4 i 6 |
| 8 | `notebooks/m4_performance_automation_cicd_orientation.ipynb` | nie tworzy nowych tabel Gold; czyta obiekty z kroków 4 i 6, orientacja Lakeflow Jobs/DABs bez live deployu |

Uwaga: `workshops/w1_gold_kpi_exercise.ipynb` i
`workshops/w2_powerbi_dataset_exercise.ipynb` (wersje z TODO dla
uczestnika) NIE są częścią tego smoke testu w pierwszej iteracji — testować
najpierw `*_solution.ipynb`, bo to one zawierają pełny, oczekiwany SQL.
Exercise warto przetestować osobno (drugi przebieg) tylko pod kątem, czy
precheck_cell faktycznie się uruchamia i czy struktura TODO nie psuje
parsowania notebooka — nie pod kątem poprawności merytorycznej (tam
poprawność = w solution).

## 3. Checklist do zweryfikowania na każdym kroku

Po każdym z 8 kroków powyżej:

### 3.1 Ogólne (każdy notebook)

- [ ] Notebook uruchamia się od góry do dołu bez błędu (`Run All`).
- [ ] Wszystkie obrazy markdown (`![...](../assets/images/...)`) renderują
      się poprawnie — brak "broken image" w UI.
- [ ] Komórka `precheck_cell` (jeśli notebook ją ma — m2, m3, m4, w1, w2)
      przechodzi bez wyjątku, gdy uruchamiana PO swoich prerequisitach.

### 3.2 Test negatywny — `precheck_cell` poza kolejnością

- [ ] Uruchomić `notebooks/m2_gold_kpi_best_practices.ipynb` PRZED
      `data/generate_training_dataset.ipynb` (np. na świeżym katalogu) —
      `precheck_cell` musi rzucić czytelny wyjątek wskazujący brakującą
      tabelę i nazwę notebooka-prerequisite (`data/generate_training_dataset.ipynb`),
      NIE może to być cichy `TABLE_OR_VIEW_NOT_FOUND` ani `AnalysisException`
      bez kontekstu.
- [ ] Powtórzyć dla `workshops/w2_powerbi_dataset_solution.ipynb`
      uruchomionego PRZED `notebooks/m3_powerbi_semantic_dataset.ipynb` —
      komunikat musi wskazywać `notebooks/m3_powerbi_semantic_dataset.ipynb`
      jako brakujący prerequisite dla `gold.v_fact_sales_incremental`.

### 3.3 Tabele istnieją i mają sensowne liczby wierszy

Po kroku 2 (generator) i kroku 4 (Module 2):

- [ ] `spark.catalog.tableExists` / `SHOW TABLES` potwierdza wszystkie 4
      tabele Silver (`sales_orders`, `order_lines`, `customers`, `products`
      — dokładne nazwy wg `docs/04-pre-implementation-analysis.md`/FND-02
      data contract w `data/generate_training_dataset.ipynb`).
- [ ] `COUNT(*)` na każdej tabeli Silver/Gold > 0 i zgodny z minimami
      zdefiniowanymi w FND-01 asercjach generatora (nie re-implementować
      progów ręcznie — po prostu potwierdzić, że asercje w generatorze same
      przeszły, czyli krok 2 zakończył się bez `AssertionError`).
- [ ] 7 kontrolowanych problemów jakości z FND-01/FND-03 faktycznie
      występuje w danych (orphan customer_id, orphan product_id, revenue
      mismatch, exact duplicate line, missing price, invalid status,
      future order date) — generator sam to assertuje na końcu, potwierdzić
      zielony wynik tych komórek.

### 3.4 Wszystkie 5 wygenerowanych obiektów BI Gold istnieją (cały kurs)

Kluczowa weryfikacja end-to-end — te 5 obiektów to finalny, dashboard-ready
output całego kursu, budowany w różnych modułach/warsztatach:

| # | Obiekt | Tworzony w | Grain |
|---|---|---|---|
| 1 | `gold.fact_sales_dashboard` | Moduł 2 (M2-02) | order line |
| 2 | `gold.fact_sales_dashboard_monthly` | Moduł 2 (M2-02) | year_month |
| 3 | `gold.fact_sales_dashboard_segment_monthly` | Moduł 2 (M2-06, **bonus**, opcjonalny) | year_month x segment |
| 4 | `gold.fact_sales_dashboard_channel_daily` | Warsztat 1 (W1-02 Zadanie 1) | order_date x channel |
| 5 | `gold.v_fact_sales_incremental` | Moduł 3 (M3-03) | order line (VIEW, nie tabela) |

Checklist:

- [ ] Wszystkie 5 obiektów istnieją po pełnym przebiegu kroków 1-7
      (`#3` jest opcjonalny/bonus — jeśli trener pominął M2-06 na żywym
      szkoleniu, brak tego obiektu jest oczekiwany, nie błąd; ale w
      smoke teście uruchomić włącznie z bonusem, żeby potwierdzić, że
      DZIAŁA, gdy ktoś go uruchomi).
- [ ] `COUNT(*)` na każdym > 0.
- [ ] Reconciliation: revenue z `gold.fact_sales_dashboard` zgadza się (w
      granicach rounding) z revenue z `gold.fact_sales_dashboard_monthly`
      zagregowanym do tego samego okresu (sprawdzane już w notebooku M2-04
      — potwierdzić, że ta komórka faktycznie przechodzi na żywych
      danych, nie tylko statycznie).
- [ ] `gold.v_fact_sales_incremental` — boundary check (`order_date =
      RangeEnd` zwraca 0 wierszy) faktycznie przechodzi na żywych danych
      (komórka istnieje w M3-03, potwierdzić wynik, nie tylko obecność
      komórki).

### 3.5 Workshopy

- [ ] `workshops/w1_gold_kpi_solution.ipynb`: wszystkie 5 zadań (Zadanie
      1-5) wykonują się bez błędu; decision log row z Zadania 5 ma
      wypełnione wszystkie kolumny (nie placeholder).
- [ ] `workshops/w2_powerbi_dataset_solution.ipynb`: wszystkie 6 zadań
      (Task 1-6) wykonują się bez błędu; BI contract (Zadanie 5) i cost
      guardrails (Zadanie 6) tabele są wypełnione, nie placeholder.

### 3.6 Moduł 4 — performance i automation orientacja

- [ ] 3 pary `EXPLAIN FORMATTED` (Silver detail vs Gold aggregate; filtr
      daty vs bez; `SELECT *` vs wybrane kolumny) wykonują się i zwracają
      realne plany zapytań z realnymi liczbami wierszy/danych zeskanowanych
      — potwierdzić, że `PushedFilters` faktycznie pojawia się w planie dla
      pary z filtrem daty (to jest sedno demo, nie tylko "komórka się
      wykonała").
- [ ] `bundle/databricks.yml` — `databricks bundle validate -t dev` NIE
      jest uruchamiane w ramach tego smoke testu notebooków (wymaga
      Databricks CLI skonfigurowanego lokalnie/w terminalu workspace, nie
      w notebooku) — jeśli trener chce to zweryfikować, to osobny krok
      poza tym planem, z jawną notatką w wyniku, czy walidacja przeszła.

### 3.7 Wizualne

- [ ] Wszystkie obrazy z `assets/images/` referencjonowane w notebookach
      renderują się poprawnie w Databricks markdown (nie tylko lokalnie w
      edytorze) — różne workspace'y czasem różnie obsługują względne
      ścieżki `../assets/images/...`, to wymaga potwierdzenia w żywym UI.

## 4. Co zrobić z wynikiem testu

Po wykonaniu tego planu na żywym workspace:

1. Zaktualizować `docs/build-log.md` nowym wpisem z realnymi wynikami
   (PASS/FAIL per krok, nie tylko "wykonano").
2. Jeśli którykolwiek krok się nie powiedzie — naprawić w
   `scripts/build_materials_v1.py` (GLOBAL-05: generator jest źródłem
   prawdy, nie edytować `.ipynb` ręcznie), zregenerować, powtórzyć smoke
   test od kroku, który zawiódł.
3. Dopiero po pełnym PASS tego planu na żywym workspace — usunąć z
   `docs/TRAINER_GUIDE.md` i z tego pliku adnotacje "nie wykonano jeszcze
   live".
