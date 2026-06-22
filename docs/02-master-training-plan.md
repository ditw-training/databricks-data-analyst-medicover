# Master plan szkolenia

## 1. Cel produktu

`Databricks-Data-Analyst-Medi` ma byc praktycznym szkoleniem end-to-end dla
analitykow danych i Power BI Developerow. Glowny rezultat szkolenia: uczestnik
umie przygotowac w Databricks warstwe Gold, zdefiniowac KPI, zweryfikowac
jakosc danych, zoptymalizowac zapytania pod BI i opisac gotowy kontrakt
raportowy.

Szkolenie nie powinno byc lista funkcji Databricks. Powinno dzialac jak
mini-projekt produkcyjny: od problemu biznesowego, przez dane i model, do
datasetu gotowego dla Power BI.

## 2. Koncepcja narracyjna

Cala narracja szkolenia opiera sie na jednym problemie:

> Zarzad potrzebuje stabilnego dashboardu KPI. Dane sa w Databricks, ale raport
> ma rozjazdy w metrykach, nie zawsze jest szybki, a zespol nie ma jasnego
> kontraktu miedzy Databricks i Power BI.

Uczestnicy przechodza przez pelny cykl:

1. Odkrywaja i profiluje dane.
2. Identyfikuja problemy jakosci i definicji.
3. Buduja warstwe Gold jako zrodlo prawdy.
4. Definiuja KPI i grain.
5. Poprawiaja wydajnosc zapytan.
6. Projektuja dataset pod Power BI.
7. Dokumentuja BI contract.
8. Decyduja, co powinno byc widokiem, tabela, agregatem lub elementem pipeline.

## 3. Scenariusz biznesowy

Domyslny scenariusz zostaje oparty na danych sprzedazowo-operacyjnych z kursu
bazowego, bo jest uniwersalny i dobrze pasuje do Power BI. Jesli `Medi` ma
oznaczac branze medyczna, scenariusz mozna latwo zamienic na medyczny bez
zmiany struktury szkolenia.

### Wariant A - sprzedaz i operacje

Artefakty biznesowe:

- sprzedaz brutto/netto,
- marza,
- liczba zamowien,
- zwroty i anulowania,
- trendy miesieczne,
- wyniki wedlug kategorii produktu, regionu i kanalu,
- jakosc danych zamowien.

### Wariant B - medyczny

Artefakty biznesowe:

- liczba wizyt,
- no-show rate,
- wykorzystanie placowek i specjalizacji,
- koszt procedur,
- SLA obslugi,
- trendy miesieczne,
- jakosc danych pacjentow, wizyt i rozliczen.

### Decyzja startowa

Na pierwsza wersje rekomendowany jest wariant A, bo bazuje na istniejacym
kontrakcie `Databricks-Data-Analyst`. Wariant B warto potraktowac jako
wersje branzy medycznej po zbudowaniu stabilnego rdzenia.

## 4. Uczestnik i obietnica szkolenia

### Dla kogo

- Data Analyst.
- BI Analyst.
- Power BI Developer.
- Osoba techniczna po stronie biznesu, ktora zna SQL i chce pracowac
  samodzielnie na Databricks.

### Po szkoleniu uczestnik potrafi

- Znalezc i zrozumiec dane potrzebne do raportowania.
- Rozroznic dane surowe, oczyszczone i raportowe.
- Zdefiniowac KPI z grain, filtrem i wlascicielem.
- Zbudowac tabele Gold pod dashboard.
- Sprawdzic, dlaczego metryki sie nie zgadzaja.
- Zaprojektowac dataset Power BI z dobrym modelem.
- Ograniczyc koszt i czas odpowiedzi zapytan BI.
- Wybrac miedzy widokiem, tabela, agregatem i materializacja.
- Przygotowac BI contract i checklisty produkcyjne.

## 5. Format i filozofia prowadzenia

Szkolenie ma byc warsztatowe. Slajdy, jesli powstana, maja byc krotkimi
wizualnymi planszami, a nie klasyczna prezentacja tekstowa.

Proporcja materialu:

- 20% kontekst i decyzje architektoniczne.
- 55% praca w notebookach i SQL.
- 15% diagnoza, dyskusje i mini-zadania decyzyjne.
- 10% checklisty, dokumentowanie i podsumowania.

Zasada: kazdy blok konczy sie konkretnym artefaktem, ktory moze wejsc do
koncowego pakietu raportowego.

## 5A. Wymagania wlasciciela materialow

Te elementy sa obowiazkowe w finalnej wersji szkolenia:

1. **Pricing i koszty SQL Warehouse.** Pokazujemy, z czego sklada sie koszt,
   czym roznia sie opcje compute, kiedy warehouse pracuje, jak DirectQuery
   zwielokrotnia liczbe zapytan i jak sizing/autostop/concurrency wplywaja na
   koszt. Material ma zawierac aktualny screenshot lub asset z oficjalnej strony
   Databricks Pricing albo Pricing Calculator, przygotowany przed finalnym
   buildem.
2. **Medallion Architecture i Gold layer.** Wyjasniamy Bronze/Silver/Gold,
   wartosc warstwy Gold oraz pokazujemy praktyczne demo budowy Gold layer w
   stylu Kimball: wymiary, fakt, grain, klucze, agregaty i dobre praktyki.
3. **Realny case biznesowy.** Szkolenie ma jasno odpowiadac, po co robimy
   analize w Gold layer, jaka jest wartosc dla biznesu i dlaczego Power BI nie
   powinien byc miejscem dla calej logiki modelu.
4. **Model w Databricks, raport w Power BI.** Model semantyczny i wiekszosc
   logiki powstaje w Databricks. W Power BI pokazujemy tylko kilka miar i kilka
   wymiarow. Material ma pokazac dwa tryby: Import mode oraz live connection /
   DirectQuery. Powstanie tez mockup raportu w PNG.
5. **Automatyzacja i CI/CD przez DABs.** Orientacja ma byc praktyczna:
   dlaczego automatyzujemy, co automatyzujemy, jak Lakeflow Jobs uruchamiaja
   odswiezanie Gold/BI datasetu oraz jak DABs/Declarative Automation Bundles
   opisuja joby, srodowiska dev/test/prod i deployment.

## 6. Struktura 7h

### Foundation - przed szkoleniem

Cel: przygotowac srodowisko i dane.

Materialy:

- `setup/00_pre_config.ipynb`
- `setup/00_setup.ipynb`
- `data/generate_training_dataset.ipynb`
- `data/source_csv/*`

Artefakty:

- katalog szkoleniowy,
- schematy Bronze/Silver/Gold,
- tabele z danymi treningowymi,
- celowo wprowadzone problemy jakosci danych.

### Modul 1 - SQL Warehouse, pricing i szybka eksploracja

Czas: ok. 45 min.

Cel: uczestnik szybko wchodzi w dane, rozumie, jak pracowac analitycznie w
Databricks SQL oraz wie, jakie decyzje wplywaja na koszt SQL Warehouse.

Zakres:

- SQL Warehouse i podstawowy workflow.
- SQL Editor vs notebook.
- Pricing overview: DBU, warehouse size, serverless/pro/classic jako opcje do
  porownania na poziomie decyzyjnym.
- Koszty SQL Warehouse: kiedy placimy, co oznacza auto-stop, co zmienia
  concurrency i co robi DirectQuery.
- Screenshot/visual z oficjalnego Pricing lub Pricing Calculator.
- Szybkie profilowanie danych.
- Identyfikacja grain i podstawowych encji.
- Pierwsze pytania biznesowe.

Artefakt:

- profil danych startowych,
- kosztowy decision card: jaki warehouse dla demo, Power BI Import i
  DirectQuery,
- lista problemow do wyjasnienia,
- pierwsza wersja mapy danych.

Material:

- `notebooks/m1_sql_warehouse_notebooks.ipynb`

### Modul 2 - Medallion, Gold layer, Kimball, KPI i jakosc danych

Czas: ok. 90 min.

Cel: uczestnik buduje logiczny fundament raportowania: tabele Gold, definicje
KPI, walidacje i data quality score.

Zakres:

- Medallion Architecture: rola Bronze, Silver i Gold.
- Warstwa Gold jako kontrakt z BI.
- Realny case biznesowy: dlaczego Gold layer istnieje, kto go uzywa i jaka jest
  wartosc spoleczna/organizacyjna jednej wersji KPI.
- Kimball-style Gold layer: fakty, wymiary, grain, klucze, powtarzalne
  agregaty.
- Demo: budowa `dim_date`, `dim_product`, `dim_customer`, `fact_sales` w
  Databricks.
- Grain tabeli faktow.
- KPI dictionary.
- Walidacja metryk.
- Bad data: duplikaty, braki, statusy, zwroty, anulowania.
- Data quality score.
- Widok vs tabela jako decyzja projektowa.
- Dobre praktyki Gold layer: stabilne nazwy, jawny grain, brak `SELECT *`,
  filtry daty, komentarze, wlasciciel danych, testy zgodnosci KPI.

Artefakty:

- pierwsza tabela Gold,
- model Kimball w Gold,
- KPI dictionary,
- walidacje KPI,
- data quality score.

Material:

- `notebooks/m2_gold_kpi_best_practices.ipynb`

### Warsztat 1 - KPI w Gold

Czas: ok. 75 min.

Cel: uczestnik samodzielnie buduje zestaw analityczny KPI i broni decyzji
modelowych.

Zadania:

- przygotowac tabele Gold pod dashboard,
- zdefiniowac 3-5 KPI,
- wskazac grain,
- sprawdzic rozjazdy metryk,
- zapisac decyzje w decision log,
- przygotowac checklisty jakosci.

Artefakty:

- `gold.fact_sales_dashboard` albo odpowiednik,
- `gold.kpi_daily` / `gold.kpi_monthly`,
- `docs/kpi-dictionary.md` jako template,
- `docs/decision-log.md` jako template.

Material:

- `workshops/w1_gold_kpi_exercise.ipynb`
- `workshops/w1_gold_kpi_solution.ipynb`

### Modul 3 - Dataset i semantyka pod Power BI: Import i live

Czas: ok. 90 min.

Cel: uczestnik projektuje stabilny dataset Power BI i rozumie, co powinno byc
liczone w Databricks, a co w Power BI.

Zakres:

- Denormalizacja vs model gwiazdy.
- Relacje, grain i filtrowanie.
- Model tworzony w Databricks: fakty, wymiary, agregaty, reporting views.
- Power BI jako cienka warstwa: kilka miar, kilka wymiarow, minimalna logika.
- Import mode: kiedy wybrac, jak planowac refresh, dlaczego zwykle jest tanszy
  i stabilniejszy.
- Live connection / DirectQuery: kiedy wybrac, jak dziala query fan-out, jak
  ograniczyc koszt i latency.
- Incremental refresh.
- Query folding i ograniczanie danych.
- BI readiness checklist.
- Mockup raportu KPI w PNG: strona summary z KPI cards, trendem, breakdownem
  po regionie/kategorii i filtrem dat.

Artefakty:

- model gwiazdy,
- reporting view albo reporting table,
- porownanie Import vs DirectQuery,
- mockup raportu Power BI,
- BI contract,
- Power BI readiness checklist.

Material:

- `notebooks/m3_powerbi_semantic_dataset.ipynb`

### Warsztat 2 - Dataset Power BI z wydajnoscia produkcyjna

Czas: ok. 45 min.

Cel: uczestnik przygotowuje finalny dataset pod dashboard i ocenia jego
gotowosc produkcyjna.

Zadania:

- przygotowac dataset dashboardowy,
- ograniczyc zakres danych,
- dodac agregat pod raport,
- przygotowac kolumny pod incremental refresh,
- wypelnic BI contract,
- wskazac ryzyka kosztowe.

Artefakty:

- `gold.fact_sales_dashboard`,
- `gold.fact_sales_dashboard_monthly`,
- `gold.v_fact_sales_incremental`,
- BI contract.

Material:

- `workshops/w2_powerbi_dataset_exercise.ipynb`
- `workshops/w2_powerbi_dataset_solution.ipynb`

### Modul 4 - Performance, koszt, Lakeflow Jobs i DABs

Czas: ok. 75 min.

Cel: uczestnik rozumie, jak utrzymac dataset w sposob przewidywalny kosztowo i
operacyjnie.

Zakres:

- Czytanie planu zapytania na poziomie analityka.
- Before/after performance.
- Najczestsze antywzorce SQL pod BI.
- Koszt SQL Warehouse: sizing, auto stop, concurrency, zapytania z raportow.
- Decyzja: widok, tabela, agregat, materializacja.
- Lakeflow Jobs: po co sa, jak ulozyc DAG od walidacji przez transformacje do
  odswiezenia Gold/BI datasetu.
- Triggery: schedule, file arrival, table update, manual run.
- Repair runs i retry jako mechanizmy obnizania kosztu awarii.
- DABs / Declarative Automation Bundles: po co, jak wyglada `databricks.yml`,
  jak opisac job, parametry i targety dev/test/prod.
- Przyklad: job `refresh_gold_bi_dataset` opisany w DABs.
- Dev/test/prod i Git integration.

Artefakty:

- performance comparison,
- cost awareness checklist,
- refresh strategy,
- mini `databricks.yml` jako referencyjny przyklad,
- diagram Lakeflow Job DAG,
- report certification checklist.

Material:

- `notebooks/m4_performance_automation_cicd_orientation.ipynb`

## 7. Capstone

Capstone nie musi byc osobnym dlugim modulem. Powinien byc finalnym zadaniem,
ktore spina warsztat 2 i modul 4.

### Zadanie

Uczestnik dostaje wymaganie:

> Przygotuj dataset dla dashboardu KPI, ktory ma byc odswiezany codziennie,
> szybko filtrowac po dacie, regionie i kategorii oraz miec jasna definicje
> metryk.

### Deliverable uczestnika

- tabela lub widok raportowy,
- 3-5 KPI,
- definicje KPI,
- walidacje jakosci,
- decyzja view/table/aggregate,
- BI contract,
- refresh strategy,
- report certification checklist.

### Kryteria sukcesu

- KPI maja definicje biznesowe i techniczne.
- Grain jest jawny.
- Dataset jest filtrowalny po dacie.
- Relacje do wymiarow sa jednoznaczne.
- Wyniki sa walidowane.
- Koszt i performance sa omowione.
- Wiadomo, kto i jak utrzymuje dataset.

## 8. Elementy atrakcyjne szkoleniowo

### Bad data lab

Do datasetu trzeba wprowadzic kontrolowane problemy:

- brakujace ceny,
- duplikaty rekordow,
- anulowania i zwroty,
- statusy spoza slownika,
- rekordy z przyszla data,
- brakujace relacje do wymiarow.

Uczestnicy maja je wykryc, opisac i zdecydowac, czy poprawka nalezy do Silver,
Gold czy warstwy raportowej.

### Incident scenario

Scenariusz:

> Po nocnym odswiezeniu dashboard pokazuje inna sprzedaz niz wczoraj. Biznes
> twierdzi, ze raport jest zepsuty.

Diagnoza:

- czy zmienily sie dane,
- czy zmienila sie definicja KPI,
- czy incremental refresh pominal zakres,
- czy join zwielokrotnil rekordy,
- czy statusy zamowien zostaly policzone inaczej,
- czy raport odpytuje widok lub tabele o innej logice.

### Performance before/after

Kazdy uczestnik powinien zobaczyc porownanie:

- wolne zapytanie,
- plan i koszt,
- poprawiona wersja,
- roznica w skanach, czasie i liczbie operacji.

### Role-play biznes vs data

Krotkie cwiczenie dyskusyjne:

- biznes: "sprzedaz sie nie zgadza",
- analityk zadaje pytania,
- grupa rozdziela problem na definicje, dane, model i refresh.

## 9. Dokumenty i szablony do utworzenia

W folderze `docs/templates/` warto przygotowac:

- `kpi-dictionary.md`
- `bi-contract.md`
- `decision-log.md`
- `refresh-strategy.md`
- `report-certification-checklist.md`
- `data-quality-checklist.md`
- `cost-awareness-checklist.md`

Te dokumenty powinny byc wykorzystywane w warsztatach, nie tylko dolaczone jako
dodatek.

## 10. Wizualizacje

Klasyczne prezentacje tekstowe nie sa priorytetem. Jesli robimy decki, powinny
byc wizualne i krotkie.

### Typy wizualizacji

1. Diagram Medallion: Bronze -> Silver -> Gold -> Power BI.
2. Model gwiazdy: fact + dimensions.
3. Przeplyw KPI: zrodlo -> transformacja -> metryka -> dashboard.
4. Decyzja view vs table vs aggregate.
5. Mockup dashboardu KPI.
6. Before/after performance.
7. Incident diagnosis flow.
8. BI contract jako plansza.
9. Report certification checklist jako plansza.
10. Pricing/cost comparison dla SQL Warehouse.
11. Import vs DirectQuery flow.
12. Lakeflow Jobs DAG i DABs deployment flow.

### Jak je tworzyc

Rekomendowany sposob:

- diagramy techniczne: Mermaid, Graphviz albo Python,
- mockupy dashboardow: HTML/CSS/SVG eksportowane do PNG,
- plansze checklist: HTML/CSS albo PPTX generowany z kodu,
- pricing screenshot: aktualny zrzut z oficjalnej strony Databricks Pricing /
  Pricing Calculator lub Azure pricing page, z data wykonania,
- obrazy AI: tylko okladka lub ilustracja kontekstowa, nie diagramy techniczne.

Powod: diagramy i mockupy musza byc czytelne, poprawne i latwe do poprawienia.
AI-obraz moze byc atrakcyjny wizualnie, ale nie powinien byc zrodlem prawdy dla
architektury lub modelu danych.

### Decki opcjonalne

Jesli powstana prezentacje, to jako `visual decks`:

- max 8-12 slajdow na caly dzien albo 3-5 plansz na modul,
- minimalna ilosc tekstu,
- jeden mocny diagram lub mockup na slajd,
- deck wspiera narracje, ale notebook jest glownym materialem.

## 11. Repozytorium raportowe jako artefakt

W trakcie szkolenia warto pokazac minimalny wzorzec repo raportowego:

```text
reporting-project/
├── sql/
│   ├── gold/
│   ├── validation/
│   └── performance/
├── docs/
│   ├── kpi-dictionary.md
│   ├── bi-contract.md
│   ├── decision-log.md
│   ├── refresh-strategy.md
│   └── report-certification-checklist.md
└── README.md
```

To pokazuje uczestnikom, ze raport to nie tylko zapytanie SQL, ale utrzymywalny
produkt danych.

## 12. Kontrakt danych

W pierwszej iteracji wykorzystujemy kontrakt z kursu bazowego:

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

Rozszerzenia dla wersji Medi:

- tabela lub widok jakosci danych,
- dashboard fact/reporting table,
- agregat miesieczny,
- widok pod incremental refresh,
- slownik KPI jako dokument i/lub tabela.
- job do odswiezania Gold/BI datasetu,
- bundle/DABs z targetami dev/test/prod jako przyklad referencyjny.

## 13. Plan budowy materialow

### Etap 1 - Foundation

- Skopiowac i odchudzic setup z `Databricks-Data-Analyst`.
- Skopiowac zrodla CSV.
- Przygotowac generator danych.
- Dodac kontrolowane problemy jakosci danych.
- Zweryfikowac statycznie notebooki setupu.

### Etap 1A - Pricing i assety kosztowe

- Zweryfikowac aktualna strone Databricks Pricing i Pricing Calculator.
- Jesli szkolenie jest prowadzone na Azure, sprawdzic Azure Databricks pricing
  jako dodatkowe zrodlo.
- Przygotowac screenshot pricingu lub kalkulatora jako asset.
- Przygotowac uproszczona plansze: warehouse size, auto-stop, concurrency,
  Import vs DirectQuery, job compute vs SQL Warehouse.

### Etap 2 - Szablony i dokumenty produkcyjne

- Utworzyc `docs/templates/*`.
- Zdefiniowac BI contract.
- Zdefiniowac KPI dictionary.
- Zdefiniowac checklisty.

### Etap 3 - Modul 1

- Zbudowac notebook eksploracyjny.
- Dodac pierwsze profilowanie danych.
- Dodac krotki artifact: data map.

### Etap 4 - Modul 2 i warsztat 1

- Zbudowac notebook Medallion/Gold/KPI.
- Dodac wyjasnienie Gold layer i realny case biznesowy.
- Dodac demo Kimball-style Gold layer.
- Dodac data quality score.
- Dodac bad data lab.
- Zbudowac warsztat `exercise` i `solution`.

### Etap 5 - Modul 3 i warsztat 2

- Zbudowac model Power BI.
- Przygotowac mockup raportu w PNG.
- Pokazac wariant Import mode.
- Pokazac wariant live connection / DirectQuery.
- Dodac BI readiness checklist.
- Dodac incremental refresh readiness.
- Zbudowac warsztat `exercise` i `solution`.

### Etap 6 - Modul 4

- Dodac performance before/after.
- Dodac cost awareness.
- Dodac incident scenario.
- Dodac Lakeflow Jobs jako praktyczny model automatyzacji.
- Dodac DABs/Declarative Automation Bundles jako model CI/CD.
- Dodac przyklad `databricks.yml`.

### Etap 7 - Wizualizacje

- Wygenerowac diagramy techniczne.
- Zbudowac mockup dashboardu.
- Zdecydowac, czy tworzymy jeden deck dzienny, czy plansze per modul.

### Etap 8 - QA

- Sprawdzic poprawnosci JSON notebookow.
- Sprawdzic Python compile dla komorek Python.
- Sprawdzic spojnosc nazw tabel i kolumn.
- Sprawdzic brak rozjazdow w kontrakcie danych.
- Zweryfikowac decki/obrazy, jesli powstana.
- Wykonac test w realnym Databricks workspace przed pierwszym szkoleniem.

## 14. Co mierzy jakosc szkolenia

Szkolenie jest dobre, jesli uczestnik po jego zakonczeniu moze odpowiedziec na
pytania:

- Co jest zrodlem prawdy dla KPI?
- Jaki jest grain tabeli raportowej?
- Dlaczego dwa raporty moga pokazac inne wyniki?
- Czy dataset nadaje sie do Power BI?
- Co powinno byc liczone w Databricks, a co w Power BI?
- Kiedy wybrac Import, a kiedy live connection / DirectQuery?
- Kiedy uzyc widoku, tabeli lub agregatu?
- Jak ograniczyc koszt zapytan BI?
- Jak dobrac i kontrolowac koszt SQL Warehouse?
- Jak opisac refresh i wlascicielstwo raportu?
- Co daje Lakeflow Job i co daje DABs?
- Jak zdiagnozowac incydent z blednym dashboardem?

## 15. Decyzje do potwierdzenia

Przed budowa pelnej zawartosci trzeba potwierdzic:

1. Czy zostajemy przy scenariuszu sprzedazowym, czy robimy wariant medyczny.
2. Czy Power BI ma byc tylko omawiany, czy uczestnicy beda laczyc sie z Power BI
   Desktop.
3. Czy pricing pokazujemy dla Databricks global pricing, Azure Databricks, czy
   obu wariantow.
4. Czy tworzymy wizualny deck, czy tylko obrazy/diagramy osadzone w notebookach.
5. Czy capstone ma byc obowiazkowy, czy traktowany jako podsumowanie dla
   szybszych grup.
6. Czy finalny kurs ma pozostac w 7 godzinach, czy dopuszczamy wariant 1,5 dnia.
