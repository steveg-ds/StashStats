# Implementation Plan: Replace SQLite with PostgreSQL and migrate data

## Phase 0: Workspace Setup & Pre-requisites

- [ ] Task: Install Postgres dependencies
    - [ ] Add `psycopg2-binary` to `requirements.txt` (or update pip dependencies in `.venv`)

## Phase 1: Database Manager & Schema Implementation

- [ ] Task: Implement Postgres DBManager and schema creation
    - [ ] Write unit tests for `DBManager` schema creation and basic queries using mock database connections
    - [ ] Modify `stashies/db.py` to replace `sqlite3` with `psycopg2` connection pool
    - [ ] Update column types in schema (`VARCHAR(50)`, `DOUBLE PRECISION`, `SERIAL PRIMARY KEY`) and query placeholders to `%s`
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Database Manager & Schema Implementation' (Protocol in workflow.md)

## Phase 2: Docker Compose & Environment Configuration

- [ ] Task: Restore PostgreSQL service in docker-compose
    - [ ] Restore `db` service (postgres:15-alpine) and volumes in `docker-compose.yml`
    - [ ] Add depends_on relation to `web` service in docker-compose.yml
    - [ ] Ensure `DATABASE_URL` is passed to the web container and updated in `.env`
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Docker Compose & Environment Configuration' (Protocol in workflow.md)

## Phase 3: Data Migration Script

- [ ] Task: Build data migration utility
    - [ ] Write unit tests for migrating data from a mock SQLite database to a mock/real Postgres database
    - [ ] Implement `migrate_sqlite_to_postgres.py` to read SQLite records and write to PostgreSQL
    - [ ] Execute migration script and verify data integrity
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Data Migration Script' (Protocol in workflow.md)
