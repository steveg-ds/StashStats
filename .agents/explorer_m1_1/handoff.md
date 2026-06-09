# Handoff Report — Explorer 1

## 1. Observation
- **`stashies/db.py`**: Contains PostgreSQL SimpleConnectionPool initialization and query executions targeting PostgreSQL using `%s` formatting (e.g., `cur.execute("SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = %s", (stash_id,))`).
- **`stashies/model.py`**: Connects database setup via `DBManager.get_pool()` on line 145, and fetches/saves data calling:
  - `DBManager.get_stash_history(...)` (lines 171, 255)
  - `DBManager.get_original_values(...)` (lines 172, 206, 256)
  - `DBManager.save_original_values(...)` (lines 230-236)
  - `DBManager.save_history_event(...)` (lines 220-227)
- **`docker-compose.yml`**: Contains three services: `web`, `db` (image: `postgres:15-alpine`), and `cache` (image: `redis:7-alpine`). Environment variable `DATABASE_URL` is set under `web` service.
- **`requirements.txt`**: Declares `psycopg2-binary==2.9.6` on line 10.
- **`stashies/components/search_results.py`**: Form lacks a date field. Renders text/dropdown inputs and a button with ID pattern `{"type": "stash-submit-btn", "index": id}`.
- **`stashies/components/edit_modal.py`**: Contains Tab 2 ("Log Usage") with an input ID `"edit-stash-used-skeins"`, lacking any date entry element.
- **`app.py`**: Declares Dash callbacks routing `stash-submit-btn` clicks and `edit-stash-save-btn` clicks, neither passing date picker values currently.

---

## 2. Logic Chain
1. **SQLite Migration (Items 1, 2, 3)**: Since the application references `DBManager` connection pool methods internally, we can design an emulated `SQLitePool` wrapper in `stashies/db.py` to minimize rewrite downstream. By adapting the query syntax to SQLite (placeholders `?` and table type changes), we can implement SQLite without touching queries in other modules. Since PostgreSQL is removed, we drop `psycopg2-binary` from `requirements.txt` and remove the `db` service container block from `docker-compose.yml`.
2. **Concurrency Control (Item 4)**: SQLite is prone to locking/busy issues under multi-process write workloads. Transitioning the Gunicorn CMD from default processes to `--workers 1 --threads 4` guarantees that only one process accesses the SQLite file, avoiding write collisions while handling concurrency inside threads.
3. **Username Collision Fix (Item 5)**: Linux shells automatically inject the shell environment variable `USERNAME`, which collides with Ravelry's `USERNAME` field if a fallback is utilized. Renaming this key globally to `RAVELRY_USERNAME` prevents system-level collisions.
4. **Lightweight Multi-Stage Dockerfile (Item 6)**: Transitioning from single-stage to a multi-stage `Dockerfile` allows caching PIP dependencies in a separate virtual environment `/opt/venv` inside a build container. The final runtime container copies only this virtual environment and the code structure, eliminating bulky compiler tools.
5. **DatePicker Implementation & Wiring (Items 7, 8)**: To handle custom date values:
   - We insert `dcc.DatePickerSingle` components in the Dash components.
   - We update the corresponding callback signatures in `app.py` to fetch their state values.
   - During stash log usage edits, the selected custom `usage_date` needs to be linked to the backend `get_stash_list` database synchronization. We can store this custom date in-memory inside the single-process Gunicorn container via a class dictionary registry `DBManager._pending_dates` and fetch/pop it during cache sync.

---

## 3. Caveats
- The application currently relies on a dynamic cache invalidation pattern. If the app is scaled horizontally to multiple hosts, the class-level dictionary in-memory registry `_pending_dates` will not be shared across hosts. However, given that this is a single-user system designed to run on a single host with a single container (using `--workers 1`), this in-memory registry is completely safe and appropriate.

---

## 4. Conclusion
We have formulated a complete strategy and exact code modifications for replacing PostgreSQL with SQLite, cleaning up Docker Compose configuration, applying lightweight multi-stage Docker builds, fixing the username collisions, and adding DatePickers in Dash. All changes have been written to `findings.md`.

---

## 5. Verification Method
1. **Local Pytest validation**:
   Run `.venv/bin/pytest tests/test_e2e.py` to confirm mock database and app flows pass without errors.
2. **Docker validation**:
   Run `docker compose up --build -d` and inspect that only `web` and `cache` services start up successfully.
3. **Database inspection**:
   Run `docker exec -it stashstats-web-1 sqlite3 /app/data/stash.db ".tables"` to verify SQLite tables `original_values` and `stash_history` are created on startup.
