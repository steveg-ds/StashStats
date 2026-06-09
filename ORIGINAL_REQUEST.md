# Original User Request

## Initial Request — 2026-06-09T01:13:28-05:00

Refactor the StashStats Plotly Dash app to replace PostgreSQL with SQLite, fix three bugs, and add two date-picker UI fields. The app is a personal yarn stash tracker that wraps the Ravelry API, runs in Docker Compose (web + Redis cache), and is used by one person.

Working directory: /home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup
Integrity mode: development

---

## Codebase Context

Key files:
- `app.py` — Dash app entrypoint, all callbacks
- `stashies/model.py` — Ravelry API calls, Redis caching
- `stashies/db.py` — Database manager (currently PostgreSQL/psycopg2 — must be rewritten)
- `stashies/app_controller.py` — Controller wiring model to UI
- `stashies/components/search_results.py` — Yarn search result accordion + inline stash-add form
- `stashies/components/edit_modal.py` — Edit/log usage modal
- `docker-compose.yml`, `Dockerfile`, `requirements.txt`, `.env.example`

Current state: App runs in Docker Compose with 3 services: `web`, `db` (PostgreSQL), `cache` (Redis). Goal: eliminate `db`, use SQLite file instead.

---

## Requirements

### R1. Replace PostgreSQL with SQLite
Remove the PostgreSQL container and `psycopg2-binary` dependency. Rewrite `stashies/db.py` using Python stdlib `sqlite3`. The new implementation must:
- Store the SQLite file at the path from env var `SQLITE_DB_PATH`, defaulting to `/app/data/stash.db`
- Enable WAL journal mode (`PRAGMA journal_mode=WAL`) on every connection
- Use `check_same_thread=False`
- Preserve the exact same public interface: `get_original_values`, `save_original_values`, `get_stash_history`, `save_history_event`
- Use the same table schema (adapt syntax: `INTEGER PRIMARY KEY AUTOINCREMENT` instead of `SERIAL PRIMARY KEY`)
- Update `docker-compose.yml`: remove `db` service, remove `pgdata` volume, add `./data:/app/data` volume on `web`
- Update `requirements.txt`: remove `psycopg2-binary`
- Update `.env.example`: remove `DATABASE_URL`
- Gunicorn CMD must use `--workers 1 --threads 4` to avoid SQLite multi-process contention

### R2. Fix USERNAME Environment Variable
All occurrences of `os.getenv("USERNAME")` in `model.py` and `app_controller.py` must be replaced with `os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")`. Update `docker-compose.yml` to pass `RAVELRY_USERNAME` instead of `USERNAME`. Update `.env.example` accordingly.

### R3. Fix Analytics Plots (prevent_initial_callbacks race)
The analytics tab currently shows an empty div because `prevent_initial_callbacks=True` on the Dash app suppresses the dropdown's initial fire when the layout is dynamically injected. Fix by merging the two analytics callbacks in `app.py` (`render_analytics_layout` and `update_analytics_content`) into a single callback that fires on tab switch to `tab-analytics` and returns the full layout including a pre-rendered graph in one response. The `analytics-metric-selector` dropdown must still trigger a re-render when changed.

### R4. Debounce Stash Filter Input
The stash filter input (`stash-search-query`) currently calls `get_stash_list()` (a full paginated Ravelry API fetch) on every keystroke. The input must be debounced so the callback only fires after the user stops typing (use `dcc.Input(debounce=True)` or equivalent). This prevents accordion state resets and reduces API calls.

### R5. Cache Uncached API Calls in Redis
Add Redis caching (with appropriate TTLs) in `model.py` for:
- `get_full_yarn(yarn_id)`: cache key `yarn:{yarn_id}`, TTL 24 hours
- `get_project_map()`: cache key `proj_map:{username}`, TTL 10 minutes
- The full paginated stash list in `get_stash_list()`: cache key `stash_list:{username}`, TTL 5 minutes (cache the raw list before per-item enrichment; invalidate on `update_stash` call)

### R6. Add Date Pickers
Two new `dcc.DatePickerSingle` components, both defaulting to `datetime.date.today().isoformat()` with `display_format="YYYY-MM-DD"`:
1. **Stash-add form** (`search_results.py`): Add after the existing input rows. ID pattern: `{"type": "stash-date-added", "index": <yarn_id>}`. This date is passed to Ravelry as `pack.purchased_date` (YYYY-MM-DD) when creating the stash entry.
2. **Log Usage modal tab** (`edit_modal.py`): Add below the used-skeins input. ID: `"edit-stash-usage-date"`. This date is used as `event_date` when saving to `stash_history` in SQLite.
Wire both through `app_controller.py` and `app.py` callbacks accordingly.

### R7. Lightweight Multi-Stage Dockerfile
Replace the single-stage `Dockerfile` with a two-stage build:
- Stage 1 (`builder`): installs Python requirements into a virtual environment
- Stage 2 (`runtime`): copies only the venv and app source — no `gcc`, no `libpq-dev`, no build tools
- The final image should be smaller and contain only what's needed to run the app

---

## Dependency Order

Implement in this order to avoid blocking:
1. **Phase 1 (parallel)**: R1 infrastructure files (docker-compose, Dockerfile, requirements, .env.example) + R2 env var fix + R7 Dockerfile + `stashies/db.py` sqlite3 rewrite + `stashies/components/search_results.py` + `stashies/components/edit_modal.py`
2. **Phase 2**: `stashies/model.py` (needs db.py interface stable from Phase 1)
3. **Phase 3**: `stashies/app_controller.py` + `app.py` (needs component IDs from Phase 1 and model signature from Phase 2)

---

## Acceptance Criteria

### Infrastructure
- [ ] `docker compose up --build -d` completes without errors
- [ ] `docker compose ps` shows exactly 2 services: `stashstats-web-1` and `stashstats-cache-1` (no `db`)
- [ ] `grep -r "psycopg2" stashies/` returns no results
- [ ] `grep -r 'os.getenv("USERNAME")' .` returns no results

### SQLite
- [ ] `docker exec stashstats-web-1 ls /app/data/stash.db` exits 0 (file exists after first stash tab load)
- [ ] `docker exec stashstats-web-1 sqlite3 /app/data/stash.db ".tables"` shows `original_values` and `stash_history`

### Bug Fixes
- [ ] `curl -s -o /dev/null -w "%{http_code}" http://localhost:8050` returns `200`
- [ ] Navigating to the Stash Analytics tab renders at least one graph without any further interaction
- [ ] Stash filter: `grep -c "get_stash_list" app.py` shows the callback is debounced (triggered on value stop, not each character)

### Date Pickers
- [ ] The stash-add form accordion (search results) contains a `DatePickerSingle` component with today's date
- [ ] The log usage modal tab contains a `DatePickerSingle` component with today's date

### Image Size
- [ ] `docker images stashstats-web` shows a smaller image than the single-stage build (target: under 400MB)
