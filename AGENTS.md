# Project: ListenBrainz data warehouse (DuckDB)

## Goal
Migrate this Python+SQL ETL into a dbt project (dbt-duckdb), in small steps.
README.md describes the existing design (Medallion: bronze/silver/gold,
snowflake schema, DQ framework, audit framework). Preserve its behaviour.

## Rules
- Never push to main; work only on a new branch and open a PR.
- Do not delete the existing Python/SQL code until the dbt equivalent is
  tested and the task says so.
- dbt project lives in `dbt/`; use the `test` target (throwaway DuckDB
  file), never `db/ListenBrainz.duckdb`.
- Layers: models/bronze, models/silver, models/gold. Keep existing table
  and column names (lowercase is fine).
- Builds must work in CI: use only files committed to the repo (the sample
  data in `tests/sample_data/`). Never depend on `files/incoming/dataset.txt`
  or other git-ignored files by default; the full file may only be passed
  explicitly with `--vars`.
- Every model needs entries in a schema.yml with tests.
- Keep each PR small: only what the task asks for.

## How to test
cd dbt && dbt build --target test --profiles-dir .
Report the result in the PR description.
