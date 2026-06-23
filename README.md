# Databricks Data Analyst Medicover

Repository for testing the Databricks Data Analyst Medicover training
notebooks.

## Trainer Run Order

Before the course, the trainer runs:

1. `setup/00_pre_config.ipynb`

`00_pre_config` creates one isolated catalog per participant and runs
`data/generate_training_dataset.ipynb` for every catalog by passing
`TARGET_CATALOG`.

## Participant Run Order

During the course, participants use the notebooks in this order:

1. `setup/00_setup.ipynb`
2. `notebooks/demo/day1_01_sql_warehouse_analyst_tooling.ipynb`
3. `notebooks/demo/day1_02_lakehouse_delta_gold.ipynb`
4. `notebooks/demo/day1_03_gold_modeling_for_powerbi.ipynb`
5. `notebooks/workshops/w1_gold_kpi_exercise.ipynb`
6. `notebooks/demo/day2_01_powerbi_semantic_model.ipynb`
7. `notebooks/demo/day2_02_performance_automation_cicd.ipynb`
8. `notebooks/workshops/w2_powerbi_dataset_exercise.ipynb`
9. `notebooks/demo/day2_03_aibi_dashboards_genie.ipynb`

`data/generate_training_dataset.ipynb` can also be run manually for a single
catalog if a participant environment must be rebuilt.

Solution notebooks are available in `notebooks/workshops/` for trainer
validation.

## Catalog Naming

Setup resolves the Unity Catalog name from the Databricks user:

- regular users: `retailhub_<user_name>`, for example `retailhub_jan_kowalski`
- trainer users: `retailhub_trainer`

Trainer mode is used when the Databricks user contains `trainer` or `trener`,
or when the user is `krzysztof.burejza`.

`setup/00_pre_config.ipynb` creates catalogs with `MANAGED LOCATION`. Before
running it, verify `TRAINING_GROUP` or `TRAINING_USERS`, and verify
`STORAGE_LOCATION` for the target workspace storage account/container.

## Bonus Notebooks

Three optional notebooks are available in `notebooks/bonus/`. They can be
worked through independently after the course or together with the trainer if
time allows. Each notebook builds its own isolated demo tables and cleans up
after itself.

| Notebook | Topic | Adapts from |
|---|---|---|
| `B1_data_ingestion.ipynb` | How data gets into the Lakehouse: `spark.read`, `read_files()`, CTAS, COPY INTO, Auto Loader, Lakeflow Connect | DE-Associate module 02 |
| `B2_medallion_pipeline.ipynb` | Full Bronze → Silver → Gold pipeline demo on the RetailHub dataset | DE-Associate module 06 |
| `B3_delta_lake_advanced.ipynb` | Advanced Delta Lake: Time Travel, RESTORE, MERGE INTO, constraints, OPTIMIZE/VACUUM | DE-Associate module 03 |

Prerequisites for all bonus notebooks: participant catalog provisioned and
`data/generate_training_dataset.ipynb` run (same requirement as the main
course).

## Included For Testing

```text
assets/images/        Visuals referenced by active notebooks
bundle/               Databricks Asset Bundle definition
data/                 Dataset generator notebook
docs/templates/       BI handoff templates referenced by exercises
notebooks/demo/       Demo notebooks
notebooks/workshops/  Workshop notebooks and solutions
notebooks/bonus/      Optional bonus notebooks (self-contained, clean up after themselves)
setup/                Workspace setup notebooks
```

Local build scripts, old notebooks, planning notes and presentation drafts are
ignored because they are not required to test the notebook run path.
