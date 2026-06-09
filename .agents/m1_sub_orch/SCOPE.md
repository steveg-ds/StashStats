# Scope: Milestone 1: Infrastructure & DB

## Architecture
- Database: Migration from PostgreSQL to SQLite.
- File modifications:
  - `stashies/db.py`: Rewrite to use Python `sqlite3` stdlib. Needs WAL mode, `check_same_thread=False`, exact same public interface, and table schema creation if not exists.
  - `docker-compose.yml`: Remove `db` (Postgres) service, remove `pgdata` volume, add local `data` volume for the SQLite database. Set gunicorn command to `--workers 1 --threads 4`.
  - `Dockerfile`: Replace single-stage build with a lightweight multi-stage build.
  - `requirements.txt`: Remove `psycopg2-binary`.
  - Environment variables: Replace `os.getenv("USERNAME")` with `os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")` in all files. Pass `RAVELRY_USERNAME` in docker-compose.yml, update `.env.example`.
  - `stashies/components/search_results.py`: Add `dcc.DatePickerSingle` component to stash-add form with ID `{"type": "stash-date-added", "index": <yarn_id>}` and default today's date.
  - `stashies/components/edit_modal.py`: Add `dcc.DatePickerSingle` component to Log Usage modal tab with ID `"edit-stash-usage-date"` and default today's date.

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Milestone 1 Implementation | Complete all R1, R2, R7, and R6 requirements in single iteration | none | PLANNED |

## Interface Contracts
### `stashies/db.py` ↔ Application
- Maintain the same database interface functions (e.g. connections, table queries, mutations) to keep the app working seamlessly.
