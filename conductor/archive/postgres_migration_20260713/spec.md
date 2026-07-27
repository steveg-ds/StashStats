# Specification: Replace SQLite with PostgreSQL and migrate data

## Goals
- Decouple StashStats from SQLite and migrate back to PostgreSQL as the primary database backend.
- Ensure all existing SQLite data (including original values and stash history) is migrated to the new PostgreSQL database.
- Restore the `db` service container in Docker Compose using `postgres:15-alpine`.
- Ensure type safety and TDD principles.

## Architecture
- `stashies/db.py`: Replace `sqlite3` connection handling with `psycopg2` using connection pooling.
- `docker-compose.yml`: Restore PostgreSQL service definition `db` and expose on port 5432. Restore container depends_on constraints.
- `migrate_sqlite_to_postgres.py`: A Python script to extract existing data from SQLite database and load it into PostgreSQL.

## Non-Functional Requirements
- Ensure transactions are used for all DB writes to ensure consistency.
- Robust error handling for migration script.
