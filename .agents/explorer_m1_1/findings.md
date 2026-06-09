# Strategy & Findings Report: SQLite Migration and UI Enhancements

This report provides the detailed design, exact code structure, and step-by-step implementation strategy for migrating StashStats from PostgreSQL to SQLite, streamlining the Docker configuration, and adding date-picker inputs.

---

## 1. SQLite Database Migration

### Target: `stashies/db.py`
We replace the PostgreSQL backend and `psycopg2` pool implementation with Python's standard library `sqlite3`. 
To preserve the exact public interface (`DBManager.get_pool()`, `get_original_values`, `save_original_values`, `get_stash_history`, `save_history_event`), we construct an emulated `SQLitePool` wrapper. This wrapper provides `getconn()` and `putconn(conn)` methods matching the `psycopg2.pool` interface, making the change transparent to the rest of the application.

#### Key Invariants & Features:
1. **Database Path**: Handled via `SQLITE_DB_PATH` env var, defaulting to `/app/data/stash.db`.
2. **WAL Mode**: Executed as `PRAGMA journal_mode=WAL` on every newly opened connection.
3. **check_same_thread=False**: Configured on connection startup to allow multi-threaded access.
4. **Parameter Substitution**: Adapted query placeholders from `%s` (PostgreSQL) to `?` (SQLite).
5. **Schema Adaptation**: `SERIAL PRIMARY KEY` is adapted to `INTEGER PRIMARY KEY AUTOINCREMENT`. `DOUBLE PRECISION` is replaced with `REAL`.
6. **Pending Date Registry**: A class-level dictionary `_pending_dates` stores custom `usage_date` values in-memory across the multi-threaded single-process Gunicorn container. This links the custom UI date picker value to database insertion during cache synchronization.

#### Exact Proposed Content for `stashies/db.py`:
```python
import os
import logging
import sqlite3
from typing import Optional

logger = logging.getLogger("stashies.db")

class SQLitePool:
    def __init__(self, db_path: str):
        self.db_path = db_path

    def getconn(self) -> sqlite3.Connection:
        # Establish connection with thread-safety flag
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        # Enable WAL mode for high concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def putconn(self, conn: sqlite3.Connection) -> None:
        # Close connection to release resource handles
        conn.close()

class DBManager:
    _pool = None
    _pending_dates = {}

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            db_path = os.getenv("SQLITE_DB_PATH", "/app/data/stash.db")
            # Ensure the directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            try:
                cls._pool = SQLitePool(db_path)
                logger.info(f"SQLite database initialized at {db_path}.")
                cls.run_migrations()
            except Exception as e:
                logger.error(f"Failed to initialize SQLite database: {e}")
                raise e
        return cls._pool

    @classmethod
    def run_migrations(cls):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS original_values (
                    stash_id TEXT PRIMARY KEY,
                    yards REAL NOT NULL,
                    meters REAL NOT NULL,
                    skeins REAL NOT NULL,
                    grams REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute("""
                CREATE TABLE IF NOT EXISTS stash_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stash_id TEXT NOT NULL,
                    event_date TEXT NOT NULL,
                    yards REAL NOT NULL,
                    meters REAL NOT NULL,
                    skeins REAL NOT NULL,
                    grams REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_history_stash_id ON stash_history(stash_id);
                """)
                conn.commit()
                logger.info("SQLite database migrations executed successfully.")
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            raise e
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_original_values(cls, stash_id: str):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = ?", 
                    (str(stash_id),)
                )
                row = cur.fetchone()
                if row:
                    return {"yards": row[0], "meters": row[1], "skeins": row[2], "grams": row[3]}
                return None
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error reading original_values for stash {stash_id}: {e}")
            return None
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_original_values(cls, stash_id: str, yards: float, meters: float, skeins: float, grams: float):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                INSERT INTO original_values (stash_id, yards, meters, skeins, grams)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (stash_id) DO NOTHING
                """, (str(stash_id), yards, meters, skeins, grams))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error saving original_values for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_stash_history(cls, stash_id: str):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    "SELECT event_date, yards, meters, skeins, grams FROM stash_history WHERE stash_id = ? ORDER BY id ASC", 
                    (str(stash_id),)
                )
                rows = cur.fetchall()
                history = []
                for row in rows:
                    history.append({
                        "date": row[0],
                        "yards": row[1],
                        "meters": row[2],
                        "skeins": row[3],
                        "grams": row[4]
                    })
                return history
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error reading stash_history for stash {stash_id}: {e}")
            return []
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_history_event(cls, stash_id: str, event_date: str, yards: float, meters: float, skeins: float, grams: float):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("""
                INSERT INTO stash_history (stash_id, event_date, yards, meters, skeins, grams)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (str(stash_id), event_date, yards, meters, skeins, grams))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            logger.error(f"Error saving stash_history event for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def set_pending_usage_date(cls, stash_id: str, usage_date: str):
        cls._pending_dates[str(stash_id)] = usage_date

    @classmethod
    def pop_pending_usage_date(cls, stash_id: str) -> Optional[str]:
        return cls._pending_dates.pop(str(stash_id), None)
```

---

## 2. Docker Compose Configuration Update

### Target: `docker-compose.yml`
We eliminate the PostgreSQL service (`db`) and the corresponding host-mapped `pgdata` volume. Instead, we mount a local directory (`./data`) into the container to persist the SQLite database.

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8050:8050"
    environment:
      - API_USERNAME=${API_USERNAME}
      - API_KEY=${API_KEY}
      - RAVELRY_USERNAME=${RAVELRY_USERNAME}
      - SQLITE_DB_PATH=/app/data/stash.db
      - REDIS_URL=redis://cache:6379/0
    volumes:
      - ./data:/app/data
    depends_on:
      cache:
        condition: service_started

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

volumes:
  redisdata:
```

---

## 3. Dependency Cleanups

### Target: `requirements.txt`
Delete the `psycopg2-binary` line from `requirements.txt` to remove it from the dependency tree.

```diff
- psycopg2-binary==2.9.6
```

---

## 4. Environment Variables & Gunicorn CMD Tuning

To avoid database contention (busy/locking issues) common with multi-process SQLite access, we limit the web container to a single worker process using multiple threads (`--workers 1 --threads 4`).

Set this inside the runtime CMD block of the Dockerfile:
```dockerfile
CMD ["gunicorn", "-b", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "app:server"]
```

---

## 5. USERNAME Env Var Fix (Prevent Collisions)

On Linux machines, `os.getenv("USERNAME")` resolves to the local operating system user, causing the application to search for incorrect stash spaces if not carefully set. We resolve this by renaming it globally to `RAVELRY_USERNAME`.

### Diffs for Affected Files:

#### A. `stashies/model.py`
Replace `os.getenv("USERNAME")` with `os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")`. Use the pattern `os.getenv("RAVELRY_USERNAME") or "KMLadyBugCrotchets"` to support fallback when the variable is set but empty.

```python
# Lines 124, 266, 274, 318
username = os.getenv("RAVELRY_USERNAME") or "KMLadyBugCrotchets"
```

#### B. `tests/test_e2e.py`
```python
# Line 12
os.environ.setdefault("RAVELRY_USERNAME", "test_user")

# Line 55
        env={**os.environ, "API_USERNAME": "test_user", "API_KEY": "test_key", "RAVELRY_USERNAME": "test_user"}
```

#### C. `.env.example`
Remove `USERNAME` and replace with `RAVELRY_USERNAME`. Also remove `DATABASE_URL` as it is no longer utilized.
```ini
# Ravelry API Credentials
API_USERNAME=your_personal_access_username
API_KEY=your_personal_access_password
RAVELRY_USERNAME=YourRavelryUsername

# Local dev/docker environment variables
SQLITE_DB_PATH=/app/data/stash.db
REDIS_URL=redis://cache:6379/0
```

---

## 6. Lightweight Multi-Stage Dockerfile

### Target: `Dockerfile`
A two-stage build separates the build-essential compiler tools from the minimal execution image. Since we no longer compile psycopg2 binaries, the final image size will drop well under 400MB.

```dockerfile
# Stage 1: Build virtual environment
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies needed for compiling if any packages require it
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment and install requirements
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Minimal runtime image
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application source
COPY . .

# Expose app port
EXPOSE 8050

# Run with single-worker, multi-threaded gunicorn to prevent SQLite multi-process locking
CMD ["gunicorn", "-b", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "app:server"]
```

---

## 7. Yarn Search Stash-Add Date Picker

### Target: `stashies/components/search_results.py`
1. Import `dcc` from `dash` if not already imported (e.g. `from dash import dcc, html`).
2. Import `datetime` at the top of the file.
3. Append the `DatePickerSingle` input to the form.

```python
# Imports
import datetime
from dash import dcc, html
```

```python
# Add within stash_form layout:
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Date Added"),
                                html.Br(),
                                dcc.DatePickerSingle(
                                    id={"type": "stash-date-added", "index": id},
                                    date=datetime.date.today().isoformat(),
                                    display_format="YYYY-MM-DD",
                                    className="w-100"
                                ),
                            ],
                            xs=12,
                        )
                    ],
                    className="mb-3",
                ),
```

---

## 8. Stash Edit Usage Log Date Picker

### Target: `stashies/components/edit_modal.py`
1. Import `datetime` at the top of the file.
2. Insert a new `dcc.DatePickerSingle` component in Tab 2 ("Log Usage").

```python
# Imports
import datetime
```

```python
# Insert below the Skeins Used input group and above the remaining preview:
                                                        dbc.Label("Usage Date"),
                                                        html.Br(),
                                                        dcc.DatePickerSingle(
                                                            id="edit-stash-usage-date",
                                                            date=datetime.date.today().isoformat(),
                                                            display_format="YYYY-MM-DD",
                                                            className="w-100 mb-3"
                                                        ),
```

---

## 9. Callback Plumbing (Wiring Date Values)

To make the UI inputs functional, we update the Dash callbacks and controller handlers to process the dates.

### A. Search Results Stash-Add Callback
In `app.py`, update `handle_add_to_stash` callback to receive `stash-date-added` as state and forward it:
```python
@callback(
    Output({"type": "stash-status-msg", "index": MATCH}, "children"),
    Input({"type": "stash-submit-btn", "index": MATCH}, "n_clicks"),
    State({"type": "stash-skeins", "index": MATCH}, "value"),
    State({"type": "stash-colorway", "index": MATCH}, "value"),
    State({"type": "stash-dyelot", "index": MATCH}, "value"),
    State({"type": "stash-location", "index": MATCH}, "value"),
    State({"type": "stash-notes", "index": MATCH}, "value"),
    State({"type": "stash-date-added", "index": MATCH}, "date"),
    State({"type": "stash-submit-btn", "index": MATCH}, "id"),
)
def handle_add_to_stash(n_clicks, skeins, colorway, dyelot, location, notes, date_added, button_id):
    if n_clicks is None or not n_clicks:
        raise PreventUpdate
    yarn_id = button_id["index"]
    return CONTROLLER.handle_add_to_stash(yarn_id, skeins, colorway, dyelot, location, notes, date_added)
```

In `stashies/app_controller.py`, update `handle_add_to_stash` signature and inject the date into the API payload:
```python
    def handle_add_to_stash(
        self,
        yarn_id: Union[str, int],
        skeins: Optional[float],
        colorway: Optional[str],
        dyelot: Optional[str],
        location: Optional[str],
        notes: Optional[str],
        date_added: Optional[str] = None
    ) -> str:
        stash_payload = {
            "yarn_id": int(yarn_id),
            "stash_status_id": 1
        }
        if colorway:
            stash_payload["colorway_name"] = colorway
        if dyelot:
            stash_payload["dye_lot"] = dyelot
        if location:
            stash_payload["location"] = location
        if notes:
            stash_payload["notes"] = notes
        if skeins is not None and skeins != "":
            stash_payload["pack"] = {"skeins": float(skeins)}
            if date_added:
                stash_payload["pack"]["purchased_date"] = date_added
        elif date_added:
            stash_payload["pack"] = {"purchased_date": date_added}
            
        # ... create_stash call remains identical
```

### B. Usage Log Edit Modal Callback
In `app.py`, update `save_stash_edit` callback to capture the custom usage date state:
```python
@callback(
    Output("edit-stash-status-msg", "children", allow_duplicate=True),
    Output("edit-stash-modal", "is_open", allow_duplicate=True),
    Input("edit-stash-save-btn", "n_clicks"),
    State("edit-stash-id-store", "data"),
    State("edit-stash-modal-tabs", "active_tab"),
    State("edit-stash-colorway", "value"),
    State("edit-stash-dyelot", "value"),
    State("edit-stash-location", "value"),
    State("edit-stash-notes", "value"),
    State("edit-stash-skeins", "value"),
    State("edit-stash-status", "value"),
    State("edit-stash-used-skeins", "value"),
    State("edit-stash-current-skeins-store", "data"),
    State("edit-stash-usage-date", "date"),
    prevent_initial_call=True,
)
def save_stash_edit(n_clicks, stash_id, active_tab,
                    colorway, dyelot, location, notes, skeins, status_id,
                    used_skeins, current_skeins, usage_date):
    if not n_clicks or not stash_id:
        raise PreventUpdate
    return CONTROLLER.handle_save_edit(
        stash_id, active_tab, colorway, dyelot, location, notes,
        skeins, status_id, used_skeins, current_skeins, usage_date
    )
```

In `stashies/app_controller.py`, update `handle_save_edit` to registry the pending date on usage logs before API update, and update `stashies/model.py` to pop the registered date during the subsequent cache synchronization delta check.

#### In `stashies/app_controller.py`:
```python
    def handle_save_edit(
        self,
        stash_id: Union[str, int],
        active_tab: str,
        colorway: Optional[str],
        dyelot: Optional[str],
        location: Optional[str],
        notes: Optional[str],
        skeins: Optional[float],
        status_id: Optional[int],
        used_skeins: Optional[float],
        current_skeins: Optional[float],
        usage_date: Optional[str] = None
    ) -> Tuple[str, bool]:
        if active_tab == "modal-tab-usage":
            if used_skeins is None:
                return "Enter an amount used first.", True
            current = float(current_skeins or 0)
            used_f = float(used_skeins)
            if used_f < 0:
                return "Amount used can't be negative.", True
            remaining = max(0.0, current - used_f)
            payload = {"pack": {"skeins": remaining}}
            
            # Register the usage date in-memory so the cache synchronization loop maps the history event to it
            if usage_date:
                from .db import DBManager
                DBManager.set_pending_usage_date(stash_id, usage_date)
                
            try:
                result = self.MODEL.update_stash(stash_id, payload)
                if result and "stash" in result:
                    self.LOGGER.info(f"[WRITE] stash_id={stash_id} | usage | used={used_f} remaining={remaining}")
                    return f"Saved! {used_f:.2g} skeins used → {remaining:.2g} remaining. Refresh stash tab to update list.", False
                else:
                    self.LOGGER.warning(f"[WRITE FAILED] stash_id={stash_id} | usage | payload={payload}")
                    return "Save failed — check logs.", True
            except Exception as e:
                self.LOGGER.error(f"[WRITE ERROR] stash_id={stash_id} | {e}")
                return f"Error: {e}", True
        else:
            # Details tab save logic remains unchanged...
```

#### In `stashies/model.py`:
In the `get_stash_list` method, pop the pending usage date and use it as `event_date` if present:
```python
                    old_totals = DBManager.get_original_values(s_id_str)
                    
                    if old_totals:
                        delta = {
                            "yards": new_totals["yards"] - old_totals["yards"],
                            "meters": new_totals["meters"] - old_totals["meters"],
                            "skeins": new_totals["skeins"] - old_totals["skeins"],
                            "grams": new_totals["grams"] - old_totals["grams"]
                        }
                        
                        if any(val != 0.0 for val in delta.values()):
                            # Retrieve user-selected usage date if registered, fallback to Ravelry's updated_at
                            pending_date = DBManager.pop_pending_usage_date(s_id_str)
                            if pending_date:
                                date_part = pending_date
                            else:
                                up_date_str = stash_detail.get("updated_at") or ""
                                date_part = up_date_str.split(" ")[0].replace("/", "-") if up_date_str else ""
                                
                            DBManager.save_history_event(
                                stash_id=s_id_str,
                                event_date=date_part,
                                yards=delta["yards"],
                                meters=delta["meters"],
                                skeins=delta["skeins"],
                                grams=delta["grams"]
                            )
```

Additionally, update `toggle_edit_modal` inside `app.py` to reset the `edit-stash-usage-date` value back to today when the modal is toggled open (lines 114-138):
```python
# Output:
Output("edit-stash-usage-date", "date")

# Return values in stashies/app_controller.py's toggle_edit_modal method:
# On cancel / close:
return False, no_update, no_update, no_update, no_update, no_update, no_update, no_update, no_update, "", None, "modal-tab-details", datetime.date.today().isoformat()
# On open:
return True, sd.get("id"), current_skeins, ..., datetime.date.today().isoformat()
```
*(Make sure to import datetime inside `app_controller.py` as well to support this).*

---

## 10. Step-by-Step Implementation Sequence

1. **Phase 1: Database Migration**:
   - Replace the content of `stashies/db.py` with the SQLite code.
   - Delete `psycopg2-binary` from `requirements.txt`.
2. **Phase 2: Global Username Update**:
   - Replace occurrences of `os.getenv("USERNAME")` with `os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")` in `stashies/model.py`.
   - Update tests in `tests/test_e2e.py` to use `RAVELRY_USERNAME`.
3. **Phase 3: Docker & Compose Optimization**:
   - Apply the multi-stage build structure to the `Dockerfile`.
   - Rewrite `docker-compose.yml` to remove the database service and add the SQLite mount volume.
   - Update `.env.example` file.
4. **Phase 4: Component Updates**:
   - Edit `stashies/components/search_results.py` to insert the add-form `DatePickerSingle` with the index pattern.
   - Edit `stashies/components/edit_modal.py` to insert the log-usage `DatePickerSingle`.
5. **Phase 5: Controller & Callback Plumbing**:
   - Wire the additional inputs into `app.py` callbacks.
   - Wire the date logic in `stashies/app_controller.py` and `stashies/model.py`.
6. **Phase 6: Verification**:
   - Spin up container stack and run Playwright/pytest verification suite.
