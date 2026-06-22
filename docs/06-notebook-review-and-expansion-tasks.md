# Notebook review and expansion tasks

## 1. Executive summary

Obecny build jest dobrym szkieletem, ale nie jest jeszcze pelnym materialem na
7 godzin szkolenia. Po porownaniu z notebookami z `Databricks-Data-Analyst`,
`dbx-ana` i `databricks-data-engineer-associate` widac, ze nasze notebooki sa
okolo 3-6 razy krotsze niz notebooki uzywane w pelnych szkoleniach.

W trakcie przegladu znaleziono i naprawiono dwa krytyczne bledy wykonania:

1. `data/generate_training_dataset.ipynb` tworzyl `silver.order_lines` bez
   `customer_id`, a pozniej `gold.fact_sales` probowal czytac `l.customer_id`.
2. `notebooks/m2_gold_kpi_best_practices.ipynb` uzywal `unit_price` w data
   quality check, ale `gold.fact_sales_dashboard` nie zawieral tej kolumny.

Po naprawie notebooki przechodza lokalna walidacje JSON i kompilacje komorek
Python. Nadal wymagaja live testu w Databricks.

## 1A. Status po rozbudowie wizualnej i materialowej

Po kolejnej iteracji generatora material zostal istotnie rozszerzony. To nadal
wymaga live smoke testu w Databricks, ale lokalnie build jest spojny.

Aktualne metryki po regeneracji:

| Notebook | Cells | Zmiana |
|---|---:|---|
| `m1_sql_warehouse_notebooks.ipynb` | 20 | dodano UI screenshots, source map, pre-check, risk scan, cost exercise |
| `m2_gold_kpi_best_practices.ipynb` | 26 | dodano business case, star-vs-flat, grain checks, KPI flow, reconciliation, quality gate, lineage |
| `m3_powerbi_semantic_dataset.ipynb` | 17 | dodano connector screenshot, connection walkthrough, incremental refresh, dataset plan |
| `m4_performance_automation_cicd_orientation.ipynb` | 15 | dodano query profile map, optimization checklist, automation checklist, long-form prompts |
| `w1_gold_kpi_exercise.ipynb` | 16 | dodano success criteria, pre-check, expected outputs, bonus |
| `w1_gold_kpi_solution.ipynb` | 19 | dodano pelniejsze rozwiazanie i self-check |
| `w2_powerbi_dataset_exercise.ipynb` | 14 | dodano success criteria, pre-check, expected outputs, bonus |
| `w2_powerbi_dataset_solution.ipynb` | 17 | dodano BI contract, incremental window i self-check |

Nowy pakiet ma wiecej materialu niz minimalne 7h, szczegolnie jesli trener
wykorzysta sekcje dyskusyjne, bonusy i porownania before/after. Najwazniejszy
otwarty punkt pozostaje bez zmian: uruchomienie end-to-end w realnym
Databricks workspace.

## 2. Metryki obecnych notebookow

| Notebook | Cells | Markdown | Code | Chars | Ocena tresci |
|---|---:|---:|---:|---:|---|
| `data/generate_training_dataset.ipynb` | 10 | 4 | 6 | ~7.0k | solidny foundation, ale wymaga walidacji runtime |
| `m1_sql_warehouse_notebooks.ipynb` | 10 | 5 | 5 | ~2.2k | za krotki na 45 min |
| `m2_gold_kpi_best_practices.ipynb` | 10 | 6 | 4 | ~3.9k | za krotki na 90 min, rdzen do rozbudowy |
| `m3_powerbi_semantic_dataset.ipynb` | 7 | 4 | 3 | ~1.9k | za krotki na 90 min |
| `m4_performance_automation_cicd_orientation.ipynb` | 8 | 5 | 3 | ~1.6k | za krotki na 75 min |
| `w1_gold_kpi_exercise.ipynb` | 5 | 2 | 3 | ~0.8k | za plytki warsztat |
| `w1_gold_kpi_solution.ipynb` | 6 | 3 | 3 | ~1.3k | dziala tylko jako mini-solution |
| `w2_powerbi_dataset_exercise.ipynb` | 5 | 2 | 3 | ~0.7k | za plytki warsztat |
| `w2_powerbi_dataset_solution.ipynb` | 6 | 3 | 3 | ~1.0k | dziala tylko jako mini-solution |

Dla porownania, pelne notebooki z serii maja zwykle:

- 19-28 komorek,
- 12k-20k znakow,
- kilka sekcji koncepcyjnych,
- kilka sekcji hands-on,
- recap, decision points i bonus.

## 3. Realistyczna ocena czasu

Obecny material daje prawdopodobnie:

- Foundation: 20-30 min pracy trenera, nie uczestnikow.
- Module 1: 20-25 min.
- Module 2: 35-45 min.
- Workshop 1: 20-30 min.
- Module 3: 25-35 min.
- Workshop 2: 15-25 min.
- Module 4: 25-35 min.

Razem: okolo 2.5-3.5h efektywnej tresci, zależnie od tempa i dyskusji.

Do 7h brakuje glownie:

- glebszych wyjasnien,
- wiekszej liczby cwiczen,
- pre-checkow i walidacji,
- scenariuszy decyzyjnych,
- porownan before/after,
- realnych mini-zadan w warsztatach,
- trainer notes i dyskusji prowadzonych.

## 4. Czy warsztaty dzialaja?

### Status po poprawkach

Statycznie: tak, notebooki sa poprawnym JSON i komorki Python sie kompilują.

Runtime w Databricks: niepotwierdzone, wymaga live smoke testu.

### Warunki uruchomienia

`w1_gold_kpi_*` wymaga:

1. `setup/00_pre_config.ipynb`
2. `data/generate_training_dataset.ipynb`
3. `notebooks/m2_gold_kpi_best_practices.ipynb`

`w2_powerbi_dataset_*` wymaga:

1. `setup/00_pre_config.ipynb`
2. `data/generate_training_dataset.ipynb`
3. `notebooks/m2_gold_kpi_best_practices.ipynb`
4. `notebooks/m3_powerbi_semantic_dataset.ipynb`

Wazne: `w2` nie zadziala po samym module 2, bo potrzebuje
`gold.v_fact_sales_incremental`, ktory tworzy dopiero modul 3.

### Problemy warsztatow

- `exercise` notebooki maja tylko po 2 realne zadania kodowe.
- Zadania sa raczej placeholderami niz pelnym warsztatem.
- Brakuje pre-checkow obiektow wejsciowych.
- Brakuje sekcji "expected output".
- Brakuje rubric / kryteriow sukcesu.
- Brakuje pracy z szablonami `docs/templates/*` w samym notebooku.
- Brakuje wariantow dla szybszych uczestnikow.

## 5. Task backlog notebook po notebooku

### Foundation

**FND-01 — Dodac runtime pre-check po generatorze**

- Sprawdzic, czy wszystkie tabele Silver i Gold istnieja.
- Sprawdzic minimalna liczbe rekordow.
- Sprawdzic, czy kontrolowane problemy jakosci faktycznie wystepuja.

**FND-02 — Dodac jawny data contract**

- W generatorze dodac markdown z tabela: object, grain, key columns, owner.
- Dodac `DESCRIBE TABLE` albo `SHOW COLUMNS` dla kluczowych obiektow.

**FND-03 — Rozszerzyc bad data lab**

- Dodac orphan customer/product references.
- Dodac revenue mismatch header vs lines.
- Dodac przyklad duplikatu na tym samym `order_id` i `product_id`.

**FND-04 — Dodac table comments**

- Uzyc `COMMENT ON TABLE` / `COMMENT ON COLUMN`, jesli runtime Databricks to
  wspiera w docelowym warehouse.

### Module 1 — SQL Warehouse, pricing and profiling

**M1-01 — Rozbudowac pricing/cost section**

- Dodac porownanie serverless/pro/classic na poziomie decyzyjnym.
- Dodac workflow: gdzie w UI znalezc Warehouse size, auto-stop, query history.
- Dodac task: wybierz ustawienia warehouse dla Import vs DirectQuery demo.

**M1-02 — Dodac SQL Warehouse hands-on**

- `SHOW TABLES`, `DESCRIBE DETAIL`, `DESCRIBE HISTORY`.
- Profilowanie min/max/nulls/status distribution.
- Query z filtrem daty vs bez filtra.

**M1-03 — Dodac business discovery exercise**

- Uczestnik wypelnia data map.
- Uczestnik wskazuje grain i ryzyka KPI.
- Uczestnik identyfikuje 3 pytania do biznesu.

**M1-04 — Dodac mini quiz decyzyjny**

- Kiedy SQL Editor, kiedy notebook?
- Kiedy Import, kiedy DirectQuery?
- Kiedy zadac pytanie o definicje KPI?

Target po rozbudowie: 18-22 komorki, 45-60 min.

### Module 2 — Medallion, Gold, Kimball, KPI

**M2-01 — Rozbudowac Medallion explanation**

- Bronze/Silver/Gold: ownership, quality, latency, consumers.
- Co nie powinno trafic do Gold.
- Jak Gold rozni sie od widoku roboczego analityka.

**M2-02 — Dodac Kimball step-by-step**

- Najpierw pokazac grain.
- Potem zbudowac `dim_date`, `dim_customer`, `dim_product`.
- Dopiero potem zbudowac `fact_sales_dashboard`.
- Dodac diagram relacji jako punkt odniesienia.

**M2-03 — Dodac KPI dictionary jako prace w notebooku**

- Zbudowac tymczasowa tabela/markdown z KPI.
- Revenue, Gross Margin, Return Rate, Orders, DQ Score.
- Dodac business definition i SQL definition.

**M2-04 — Dodac reconciliation checks**

- Porownac revenue z `gold.fact_sales` vs `gold.fact_sales_dashboard`.
- Pokazac jak zly join zmienia wynik.
- Pokazac problem z `COUNT(DISTINCT)` na zlym grain.

**M2-05 — Rozbudowac data quality score**

- Dodac breakdown i progi.
- Dodac sample rows dla kazdego issue.
- Dodac decyzje: poprawic w Silver, Gold czy raporcie?

**M2-06 — Dodac bonus**

- Metric view albo materialized aggregate jako temat dla szybszych grup.

Target po rozbudowie: 24-30 komorek, 90-110 min.

### Workshop 1 — Gold KPI package

**W1-01 — Dodac pre-check**

- Sprawdzic, czy `gold.fact_sales_dashboard` istnieje.
- Jesli nie istnieje, pokazac komunikat: uruchom modul 2.

**W1-02 — Rozbic warsztat na 5 zadan**

1. Zbuduj/uzupelnij reporting table.
2. Zdefiniuj KPI.
3. Znajdz data quality issues.
4. Zrob reconciliation.
5. Wypelnij decision log.

**W1-03 — Dodac expected outputs**

- Oczekiwane kolumny.
- Oczekiwane typy problemow.
- Minimalne kryteria sukcesu.

**W1-04 — Rozbudowac solution**

- Pelna wersja SQL.
- Komentarze dlaczego.
- Alternatywne odpowiedzi.

Target po rozbudowie: 14-18 komorek exercise, 16-22 komorki solution, 60-75 min.

### Module 3 — Power BI semantic dataset

**M3-01 — Rozbudowac Import vs DirectQuery**

- Tabela decyzyjna.
- Query fan-out.
- Koszt interakcji.
- Kiedy live ma sens.

**M3-02 — Dodac Power BI connection walkthrough**

- Uzyc istniejacego screenshotu `powerbi_directquery_connector.webp`.
- Pokazac server hostname / HTTP path na poziomie instrukcji.
- Dodac wariant bez Power BI Desktop: mock walkthrough.

**M3-03 — Dodac incremental refresh**

- RangeStart / RangeEnd.
- Half-open interval.
- Wymagania dla kolumny daty.
- Test zapytania pod partycje.

**M3-04 — Dodac BI contract w praktyce**

- Sekcja "fill this contract".
- Tabela: source object, grain, mode, refresh, owner.
- Checklist: czy dataset jest gotowy?

**M3-05 — Dodac mock report walkthrough**

- Omowic kazdy visual na `powerbi_report_mockup.png`.
- Ktora tabela odpowiada za ktory visual?
- Ktore visuals powinny isc z agregatu?

Target po rozbudowie: 22-28 komorek, 90 min.

### Workshop 2 — Power BI dataset readiness

**W2-01 — Dodac pre-check**

- Sprawdzic `gold.fact_sales_dashboard_monthly`.
- Sprawdzic `gold.v_fact_sales_incremental`.
- Jesli brakuje widoku, komunikat: uruchom modul 3.

**W2-02 — Rozbic warsztat na zadania**

1. Wybierz source dla summary page.
2. Wybierz source dla drill-through.
3. Zdefiniuj Import vs DirectQuery.
4. Zweryfikuj incremental refresh.
5. Wypelnij BI contract.
6. Wypelnij cost guardrails.

**W2-03 — Dodac solution z pelnym BI contract**

- Przykładowa wypelniona tabela.
- Uzasadnienie decyzji Import baseline / DirectQuery exception.

Target po rozbudowie: 12-16 komorek exercise, 14-18 solution, 45-60 min.

### Module 4 — Performance, automation, CI/CD

**M4-01 — Rozbudowac before/after performance**

- Nie tylko `EXPLAIN`, ale tez dwa zapytania porownawcze.
- Silver detail vs Gold aggregate.
- Bez filtra daty vs z filtrem daty.
- `SELECT *` vs wybrane kolumny.

**M4-02 — Dodac Query Profile walkthrough**

- Co trener pokazuje w UI.
- Na co patrzec: scan size, shuffle, joins, time.
- Jak powiazac Power BI visual z Query History.

**M4-03 — Rozbudowac cost guardrails**

- Warehouse sizing.
- Auto-stop.
- Tagging/budgets jako orientacja.
- DirectQuery report governance.

**M4-04 — Rozbudowac Lakeflow Jobs**

- Task types.
- Schedule / file arrival / table update.
- Retry i repair run.
- Kiedy Jobs vs Lakeflow Pipelines.

**M4-05 — Poprawic DABs example**

- Obecny `bundle/databricks.yml` jest tylko referencyjny.
- Trzeba sprawdzic aktualna skladnie CLI.
- Dodac `source: WORKSPACE` albo docelowy pattern zgodny z Databricks Bundles.
- Dodac `bundle validate` jako instrukcje, ale nie obiecywac bez testu.

Target po rozbudowie: 20-26 komorek, 75-90 min.

## 6. Globalne taski techniczne

**GLOBAL-01 — Dodac notebook pre-check helper**

Kazdy notebook powinien miec komorke sprawdzajaca wymagane tabele i dajaca
czytelny komunikat.

**GLOBAL-02 — Dodac trainer notes**

Nie w samym notebooku uczestnika jako dlugie notatki, ale w
`docs/TRAINER_GUIDE.md`:

- co mowic,
- gdzie robic demo UI,
- gdzie skracac,
- typowe bledy uczestnikow.

**GLOBAL-03 — Dodac runtime smoke test plan**

Dokladna kolejnosc uruchamiania i checklist rezultatow.

**GLOBAL-04 — Dodac pricing screenshot asset**

Plik `assets/images/databricks_pricing_YYYY-MM-DD.png` z data i notatka, ze
wymaga odswiezenia.

**GLOBAL-05 — Rozszerzyc generator materialow**

Nie edytowac samych `.ipynb` recznie bez aktualizacji
`scripts/build_materials_v1.py`, bo generator nadpisuje notebooki.

## 7. Priorytety implementacji

### Priorytet 0 — runtime correctness

- Live test foundation.
- Pre-check cells.
- Pre-checks dla warsztatow.
- Potwierdzenie `bundle/databricks.yml` jako referencyjny albo dzialajacy.

### Priorytet 1 — tresc na 7h

- Rozbudowac modul 2 i warsztat 1.
- Rozbudowac modul 3 i warsztat 2.
- Rozbudowac modul 4.
- Rozbudowac modul 1.

### Priorytet 2 — trainer experience

- Trainer guide.
- Timing.
- Skroty dla slabszych grup.
- Bonusy dla szybszych grup.

## 8. Rekomendacja

Nie rozszerzac wszystkiego naraz. Najlepsza kolejnosc:

1. Naprawic pre-checki i runtime safety.
2. Rozbudowac `m2` + `w1`, bo to rdzen szkolenia.
3. Rozbudowac `m3` + `w2`, bo to glowna wartosc dla Power BI.
4. Rozbudowac `m4`, bazujac na artefaktach z `m2/m3`.
5. Dopiero na koncu rozbudowac `m1`, zeby dobrze wprowadzal do finalnego case.
