# Analiza agendy

## Wnioski

Agenda opisuje krotkie, praktyczne szkolenie analityczne: 7 godzin, 2 sesje po
3,5 godziny. Najwazniejszy rezultat to umiejetnosc samodzielnego przygotowania
warstwy Gold/KPI oraz datasetu pod Power BI w Databricks SQL.

Nie jest to kopia pelnego `Databricks-Data-Analyst`, ktory w obecnej postaci ma
szerszy zakres: SQL scripting, kilka podejsc do modelowania, Unity Catalog,
ingestion, AI/BI Dashboards i Genie. Wersja `Medi` powinna byc zbudowana jako
skondensowana sciezka pod konkretne workflow analityka.

## Priorytety tresci

1. SQL Warehouse i orientacja w Databricks dla osob analitycznych.
2. Gold layer jako kontrakt raportowy: KPI, grain, jakosc, walidacja.
3. Performance zapytan SQL pod raportowanie.
4. Model/dataset Power BI: model gwiazdy, relacje, incremental refresh.
5. Orientacja w automatyzacji i CI/CD bez wchodzenia w pelne laboratorium.

## Co wykorzystac z kursu bazowego

- `setup/00_pre_config.ipynb` i `setup/00_setup.ipynb` jako wzorzec
  przygotowania srodowiska.
- `data/generate_training_dataset.ipynb` i `data/source_csv/` jako baza
  kontraktu danych.
- Wybrane notebooki z modulow `m1`, `m2`, `m3` i `m4` jako zrodlo tresci.
- Generator prezentacji i styl z `tools/build_pptx.py` oraz
  `scripts/presentation/`.

## Co ograniczyc lub pominac

- Pelny blok SQL scripting i stored procedures - tylko jesli agenda zostanie
  rozszerzona.
- Inmon/Data Vault/data mesh - zbyt szerokie jak na 7 godzin.
- Unity Catalog ingestion - tylko minimalny kontekst, jesli potrzebny do setupu.
- AI/BI Dashboards i Genie - poza obecna agenda.
- Pelne Jobs, Lakeflow Pipelines i CI/CD - tylko orientacja.

## Ryzyka

- Obraz agendy przekazany w rozmowie zawieral widoczne naglowki, ale szczegoly
  zostaly odtworzone z istniejacego `Databricks-Data-Analyst/docs/agenda-source.md`.
- Jesli wersja Medi ma miec specyficzny scenariusz biznesowy lub dataset, trzeba
  go dopisac przed budowa notebookow.
- 7 godzin wymaga scislego zakresu. Kazdy modul powinien miec sekcje bonusowa,
  ale material podstawowy musi miescic sie w czasie.

