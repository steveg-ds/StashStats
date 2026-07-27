# Implementation Plan: Replace SQLite with PostgreSQL and migrate data

## Phase 0: Workspace Setup & Pre-requisites

- [x] Task: Install Postgres dependencies [247b140]
    - [ ] Add `psycopg2-binary` to `requirements.txt` (or update pip dependencies in `.venv`)

## Phase 1: Database Manager & Schema Implementation [checkpoint: de3f56f]

- [x] Task: Implement Postgres DBManager and schema creation [10f443a]
    - [x] Write unit tests for `DBManager` schema creation and basic queries using mock database connections
    - [x] Modify `stashies/db.py` to replace `sqlite3` with `psycopg2` connection pool
    - [x] Update column types in schema (`VARCHAR(50)`, `DOUBLE PRECISION`, `SERIAL PRIMARY KEY`) and query placeholders to `%s`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Database Manager & Schema Implementation' (Protocol in workflow.md) [de3f56f]

## Phase 2: Docker Compose & Environment Configuration [checkpoint: 7e867b4]

- [x] Task: Restore PostgreSQL service in docker-compose [5bde8c6]
    - [x] Restore `db` service (postgres:15-alpine) and volumes in `docker-compose.yml`
    - [x] Add depends_on relation to `web` service in docker-compose.yml
    - [x] Ensure `DATABASE_URL` is passed to the web container and updated in `.env`
- [x] Task: Conductor - User Manual Verification 'Phase 2: Docker Compose & Environment Configuration' (Protocol in workflow.md) [7e867b4]

## Phase 3: Data Migration Script [checkpoint: 6486208]

- [x] Task: Build data migration utility [1819aa5]
    - [x] Write unit tests for migrating data from a mock SQLite database to a mock/real Postgres database
    - [x] Implement `migrate_sqlite_to_postgres.py` to read SQLite records and write to PostgreSQL
    - [x] Execute migration script and verify data integrity
- [x] Task: Conductor - User Manual Verification 'Phase 3: Data Migration Script' (Protocol in workflow.md) [6486208]
