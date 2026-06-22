# Program szkolenia

Kod szkolenia: DBX-ANA-MEDI

Tytul roboczy: Databricks dla Data Analyst i Power BI Developer - wersja Medi

Poziom: Podstawowy -> Sredniozaawansowany

Czas trwania: 2 sesje x 3,5 godz. (7 godz. lacznie; format 1 dzien lub 2
poldnia)

## Wstep ogolny

Szkolenie to praktyczny program dla analitykow i Power BI Developerow, ktorzy
chca samodzielnie odpowiadac na pytania biznesowe na danych w Databricks.
Uczestnicy pracuja end-to-end: od eksploracji danych i budowy logiki KPI na
warstwie Gold, przez optymalizacje zapytan SQL, po przygotowanie datasetu oraz
warstwy semantycznej pod raportowanie w Power BI.

## Przeznaczenie szkolenia

- Data Analystow pracujacych na danych sprzedazowych, produktowych i
  operacyjnych.
- Power BI Developerow przygotowujacych modele semantyczne i dashboardy KPI.
- BI Analystow, ktorzy chca uniezaleznic sie od wsparcia Data Engineering.

## Korzysci dla uczestnikow

- Rozumieja, gdzie szukac danych i co oznacza warstwa Gold w architekturze
  Medallion.
- Potrafia odpowiadac na pytania biznesowe bez wsparcia inzyniera danych.
- Samodzielnie eksploruja dane w Databricks przy uzyciu SQL i notebookow.
- Tworza wydajne zapytania analityczne i diagnozuja ich wydajnosc.
- Buduja dataset pod Power BI i przygotowuja warstwe semantyczna.
- Projektuja automatyczne odswiezanie danych i rozumieja roznice miedzy
  widokiem a tabela cykliczna.
- Znaja podstawy CI/CD i srodowisk dev/test/prod w Databricks.
- Stosuja dobre praktyki performance i cost optimization w Databricks i BI.

## Oczekiwane przygotowanie uczestnikow

- Praktyczna znajomosc SQL: `SELECT`, `JOIN`, `GROUP BY`, CTE.
- Podstawowa znajomosc Power BI: model, relacje, miary.
- Mile widziane ukonczone szkolenie wprowadzajace z Databricks lub rownowazna
  wiedza.
- Brak wymaganego doswiadczenia produkcyjnego w PySpark.

## Agenda szczegolowa

### Sesja 1 - Databricks SQL Warehouse

Modul 1 - Praca z danymi w Databricks: SQL + Notebooks, powtorzenie

- Databricks SQL: praca z SQL Warehouse.
- Databricks SQL vs Notebooks: kiedy wybrac ktore podejscie.
- Szybkie profilowanie danych pod pytania biznesowe.
- Omowienie narzedzi i interfejsu.

Modul 2 - Praca na warstwie Gold, najlepsze praktyki

- Warstwa Gold jako zrodlo prawdy dla raportowania i KPI.
- Praca na danych biznesowych: definicje KPI, grain, zgodnosc metryk.
- Optymalizacja zapytan: partition pruning, ograniczanie skanow, agregacje
  posrednie.
- Sprawdzanie jakosci danych i walidacja spojnosci wynikow.

Warsztat 1 - Budowa analitycznego zestawu KPI w Gold

Uczestnicy pracuja na danych z przykladowego scenariusza, tworza zestaw tabel
Gold, weryfikuja definicje KPI i sprawdzaja, jak zmiana modelu wplywa na wyniki
oraz wydajnosc.

### Sesja 2 - Power BI, performance i orientacja w automatyzacji

Modul 3 - Integracja z Power BI

- Przygotowanie danych pod raportowanie: denormalizacja vs model gwiazdy.
- Tworzenie datasetow: warstwa semantyczna, definicje metryk, grain i relacje.
- Performance w Power BI: ograniczanie danych, agregacje, incremental refresh.
- Praktyki SQL pod BI: query folding, redukcja kosztu zapytan, stabilnosc czasu
  odpowiedzi.

Warsztat 2 - Dataset pod Power BI z wydajnoscia produkcyjna

Uczestnicy przygotowuja dataset i model semantyczny pod dashboard KPI, testuja
agregacje oraz weryfikuja gotowosc danych do incremental refresh.

Modul 4 - Performance, automatyzacja i CI/CD, orientacja

- Jak czytac plan zapytania w Databricks SQL - przeglad.
- Dobre praktyki kosztowe: warehouse sizing, auto stop, harmonogramy i limity.
- Najczestsze antywzorce w analizie SQL i raportowaniu BI.
- Jobs i Lakeflow Pipelines: kiedy automatyzowac, widok vs tabela jako zrodlo
  dla Power BI.
- CI/CD: Databricks Asset Bundles, srodowiska dev/test/prod, Git integration.

## Zakres poza kursem podstawowym

Jobs, Lakeflow Pipelines i CI/CD sa w tej wersji omawiane orientacyjnie.
Pelna realizacja praktyczna tych tematow wymaga wariantu rozszerzonego.

