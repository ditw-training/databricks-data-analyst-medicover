# Databricks Data Analyst Medicover

Repository for testing the Databricks Data Analyst Medicover training
notebooks.

## Run Order

Use the notebooks in this order:

1. `setup/00_pre_config.ipynb`
2. `setup/00_setup.ipynb`
3. `data/generate_training_dataset.ipynb`
4. `notebooks/demo/day1_01_lakehouse_sql_gold.ipynb`
5. `notebooks/demo/day1_02_gold_modeling_for_powerbi.ipynb`
6. `notebooks/workshops/w1_gold_kpi_exercise.ipynb`
7. `notebooks/demo/day2_01_powerbi_semantic_model.ipynb`
8. `notebooks/demo/day2_02_performance_automation_cicd.ipynb`
9. `notebooks/workshops/w2_powerbi_dataset_exercise.ipynb`

Solution notebooks are available in `notebooks/workshops/` for trainer
validation.

## Included For Testing

```text
assets/images/      Visuals referenced by active notebooks
bundle/             Databricks Asset Bundle definition
data/               Dataset generator notebook
docs/templates/     BI handoff templates referenced by exercises
notebooks/demo/     Demo notebooks
notebooks/workshops Workshop notebooks and solutions
setup/              Workspace setup notebooks
```

Local build scripts, old notebooks, planning notes and presentation drafts are
ignored because they are not required to test the notebook run path.
