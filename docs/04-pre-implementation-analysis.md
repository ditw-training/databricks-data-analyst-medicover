# Analiza przed implementacja

## 1. Decyzja strategiczna v1

Pierwsza wersja szkolenia powinna zostac zbudowana jako:

> RetailHub Executive KPI Dashboard - praktyczny projekt end-to-end w
> Databricks SQL, Gold layer i Power BI.

To oznacza, ze nie budujemy ogolnego kursu o funkcjach Databricks. Budujemy
szkolenie, w ktorym kazdy modul doprowadza uczestnika do konkretnego artefaktu:
stabilnego datasetu KPI dla raportu zarzadczego.

## 2. Zakres v1

### W zakresie

- Scenariusz sprzedazowo-operacyjny RetailHub.
- SQL Warehouse, koszty, sizing, auto-stop i DirectQuery cost awareness.
- Medallion Architecture jako kontekst.
- Gold layer jako kontrakt raportowy.
- Kimball-style Gold: wymiary, fakt, grain, klucze, agregaty.
- KPI dictionary.
- Data quality checks i data quality score.
- Bad data lab.
- Power BI model tworzony glownie w Databricks.
- Power BI jako cienka warstwa raportowa.
- Import mode vs live connection / DirectQuery.
- Mockup raportu KPI w PNG.
- Before/after performance.
- Lakeflow Jobs jako orientacja automatyzacji.
- DABs / Declarative Automation Bundles jako orientacja CI/CD.
- BI contract, refresh strategy, decision log i report certification checklist.

### Poza zakresem v1

- Pelne laboratorium Lakeflow Pipelines.
- Pelne laboratorium CI/CD z realnym deployem do dev/test/prod.
- Pelny Power BI Desktop hands-on dla kazdego uczestnika.
- AI/BI Dashboards i Genie.
- Data Vault, Inmon, data mesh.
- Pelny wariant medyczny datasetu.

Te tematy moga byc rozszerzeniami po zbudowaniu stabilnej wersji podstawowej.

## 3. Docelowy efekt koncowy

Uczestnik po szkoleniu powinien miec lub rozumiec nastepujacy pakiet:

```text
RetailHub KPI Package
├── Gold model
│   ├── gold.dim_date
│   ├── gold.dim_product
│   ├── gold.dim_customer
│   ├── gold.fact_sales
│   ├── gold.fact_sales_dashboard
│   └── gold.fact_sales_dashboard_monthly
├── BI-ready views
│   └── gold.v_fact_sales_incremental
├── Validation
│   ├── KPI reconciliation checks
│   ├── data quality score
│   └── bad data diagnostics
├── Documentation
│   ├── kpi-dictionary.md
│   ├── bi-contract.md
│   ├── decision-log.md
│   ├── refresh-strategy.md
│   └── report-certification-checklist.md
└── Operations
    ├── Lakeflow Job DAG concept
    └── databricks.yml reference example
```

## 4. Gold standard raportu

Raport docelowy powinien byc prosty, ale wygladac jak realny artefakt BI.

### Strona 1 - Executive Overview

KPI cards:

- Revenue.
- Gross margin.
- Orders.
- Return rate.
- Data quality score.

Wizualizacje:

- trend revenue/margin po miesiacach,
- revenue by region,
- revenue by product category,
- tabela top categories albo top customers,
- slicery: date, region, channel, category.

### Strona 2 - Data Quality / Trust

KPI cards:

- duplicate order count,
- missing price count,
- invalid status count,
- future dated orders,
- orphan product/customer references.

Wizualizacje:

- data quality score trend,
- issues by type,
- sample records to investigate.

### Rola Power BI

Power BI nie jest miejscem, gdzie budujemy caly model. W Power BI pokazujemy:

- kilka miar,
- kilka wymiarow,
- filtry,
- interakcje,
- roznice miedzy Import i DirectQuery/live.

Model, grain, walidacja i wiekszosc logiki powstaja w Databricks.

## 5. Dane i celowe problemy jakosci

V1 powinna uzyc kontraktu danych z `Databricks-Data-Analyst`, z lekkim
rozszerzeniem o kontrolowane problemy jakosci.

### Dane bazowe

- `customers`
- `products`
- `sales_orders`
- `order_lines`

### Problemy do zaszycia w generatorze

- duplikaty wybranych zamowien,
- brakujace ceny jednostkowe,
- statusy spoza dozwolonego slownika,
- zwroty i anulowania,
- rekordy z przyszla data,
- brakujace powiazanie do produktu lub klienta,
- roznice miedzy revenue liczonym z headera i z linii.

### Cel dydaktyczny

Uczestnik ma zobaczyc, ze zly dashboard czesto nie wynika z Power BI, tylko z:

- niejasnej definicji KPI,
- niejawnego grain,
- zlego joina,
- braku walidacji,
- nieprzemyslanej decyzji view/table/aggregate,
- modelu budowanego zbyt pozno, dopiero w raporcie.

## 6. Wizualizacje do przygotowania

Priorytetem sa assety, ktore pomagaja prowadzic zajecia bez klasycznych
slajdow tekstowych.

### Obowiazkowe assety v1

1. `assets/images/medallion_to_powerbi.png`
   Bronze -> Silver -> Gold -> Power BI.
2. `assets/images/kimball_gold_model.png`
   Fakt, wymiary, grain i relacje.
3. `assets/images/powerbi_report_mockup.png`
   Mockup raportu RetailHub Executive KPI Dashboard.
4. `assets/images/import_vs_directquery.png`
   Porownanie trybow Power BI.
5. `assets/images/sql_warehouse_cost_decision.png`
   Decision card: size, auto-stop, concurrency, DirectQuery impact.
6. `assets/images/lakeflow_job_dag.png`
   Walidacja -> Gold refresh -> aggregate -> BI readiness checks.
7. `assets/images/dabs_deployment_flow.png`
   Repo -> bundle validate -> deploy dev/test/prod -> run job.

### Screenshot pricingu

Pricing jest zmienny. Screenshot powinien byc wykonany dopiero przy finalnym
buildzie materialow i zapisany z data, np.:

```text
assets/images/databricks_pricing_YYYY-MM-DD.png
```

W notebooku musi byc notatka, ze ceny nalezy odswiezyc przed prowadzeniem
szkolenia.

## 7. Modulowa implementacja

### Foundation

Zadania:

- skopiowac minimalny setup z `Databricks-Data-Analyst`,
- skopiowac potrzebne CSV,
- przygotowac generator danych,
- dodac problemy jakosci,
- przygotowac tabele Silver i startowe Gold,
- przygotowac templates dokumentow.

Ryzyko:

- generator nie moze byc zbyt skomplikowany; uczestnik ma rozumiec dane, nie
  walczyc z syntetyka.

### Modul 2 jako pierwszy merytoryczny build

Powod:

Gold/KPI/Kimball jest rdzeniem szkolenia. Modul 1, Modul 3 i Modul 4 powinny
byc budowane wokol decyzji podjetych tutaj.

Zadania:

- medallion explanation,
- business case,
- Kimball Gold demo,
- KPI dictionary,
- validation,
- data quality score,
- decyzje view/table/aggregate.

### Modul 3 jako drugi build

Powod:

Power BI zalezy od modelu Gold. Dopiero po Gold layer mozna sensownie pokazac
Import, DirectQuery/live, BI contract i raport.

Zadania:

- model dla Power BI,
- reporting table/view,
- incremental refresh readiness,
- Import vs DirectQuery decision,
- mockup raportu.

### Modul 1 jako trzeci build

Powod:

Modul 1 ma wprowadzic do danych i kosztow, ale powinien juz wiedziec, do czego
prowadzi caly kurs.

Zadania:

- SQL Warehouse workflow,
- data profiling,
- pricing/cost decision card,
- pierwsza mapa danych.

### Modul 4 jako ostatni build

Powod:

Automatyzacja i DABs powinny odnosic sie do realnych artefaktow z modulu 2 i 3.

Zadania:

- before/after performance,
- cost awareness,
- Lakeflow Job DAG,
- DABs reference `databricks.yml`,
- refresh strategy,
- production readiness.

## 8. Kolejnosc implementacji

Rekomendowana kolejnosc:

1. `Foundation + templates`
2. `Visual assets`
3. `Module 2 + Workshop 1`
4. `Module 3 + Workshop 2`
5. `Module 1`
6. `Module 4`
7. `Trainer guide`
8. `Static QA`
9. `Live Databricks smoke test`

## 9. Kryteria akceptacji v1

### Materialy

- Kazdy modul ma notebook.
- Kazdy warsztat ma `exercise` i `solution`.
- Kazdy notebook zaczyna sie od setupu i uzywa tego samego kontraktu danych.
- Kazdy modul konczy sie konkretnym artefaktem.
- Szablony dokumentow sa faktycznie uzywane w warsztatach.

### Tresc

- Jest jasny business case.
- Jest Medallion Architecture.
- Jest Kimball-style Gold demo.
- Jest pricing/cost awareness.
- Jest Import vs DirectQuery/live.
- Jest Lakeflow Jobs i DABs orientation.
- Jest report certification checklist.

### Technicznie

- Notebooki sa poprawnym JSON.
- Kod Python w komorkach niemagicznych sie kompiluje.
- Nazwy tabel i kolumn sa spojne.
- Nie ma rozjazdu miedzy master planem, notebookami i trainer guide.
- Assety graficzne istnieja i maja sensowne rozmiary.
- `databricks.yml` jest poprawny skladniowo jako przyklad.

## 10. Ryzyka przed implementacja

### Ryzyko 1 - za duzo zakresu w 7 godzin

Najwieksze ryzyko. Rozwiazanie: trzymamy Lakeflow Jobs i DABs jako orientacje,
nie pelne laby. Power BI tez traktujemy jako decyzje i demo, nie pelny desktop
hands-on dla kazdego.

### Ryzyko 2 - pricing zmienia sie w czasie

Rozwiazanie: nie wpisujemy stalych cen jako prawdy. Pokazujemy mechanike kosztu
i screenshot z data.

### Ryzyko 3 - DirectQuery wymaga dobrego srodowiska

Rozwiazanie: DirectQuery/live moze byc demo prowadzacego lub mock demo. Import
jest baseline dla uczestnikow.

### Ryzyko 4 - DABs terminologia

Databricks przechodzi z nazwy Databricks Asset Bundles do Declarative Automation
Bundles w czesci materialow. Rozwiazanie: uzywamy obu nazw przy pierwszym
wprowadzeniu i sprawdzamy aktualne docs przed finalizacja.

### Ryzyko 5 - zbyt duzo dokumentow

Rozwiazanie: templates maja byc krotkie, uzywane jako narzedzia pracy, nie jako
dodatkowe czytanki.

## 11. Rekomendacja implementacyjna

Zaczac od `Foundation + templates`, ale projektowac je pod finalny raport.
Pierwszy realny milestone powinien dowiezc:

- generator danych,
- tabele Silver,
- minimalne tabele Gold,
- kontrolowane problemy jakosci,
- `docs/templates/*`,
- pierwszy mockup raportu,
- pierwszy diagram Medallion -> Power BI.

Po tym milestone bedzie jasne, czy zakres i dataset trzymaja sie razem. Dopiero
wtedy warto generowac pelne notebooki modulowe.

