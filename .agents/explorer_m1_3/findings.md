# Project Investigation Findings: StashStats Stack Migration & UI Enhancements

This report covers the read-only investigation and complete implementation strategy for moving from PostgreSQL to SQLite, optimizing the Docker setup, correcting Ravelry username variable calls, and adding date pickers to UI layouts.

---

## 1. Replace PostgreSQL with SQLite (`stashies/db.py`)
- **Problem**: Decouple the app from PostgreSQL, remove psycopg2 compilation requirements, and use python's stdlib `sqlite3` module.
- **Proposed Solution**: 
  - Rewrite `stashies/db.py` to use `sqlite3`.
  - Open connections with `check_same_thread=False` and execute `PRAGMA journal_mode=WAL;` to activate WAL mode.
  - Implement a thread-safe connection-wrapper (`SQLiteConnectionPool`) mimicking `SimpleConnectionPool` to guarantee backward compatibility with the existing public interface (`get_pool()`, `getconn()`, `putconn()`).
  - Convert psycopg2 style parameter placeholders `%s` to SQLite style `?`.
  - Rewrite PostgreSQL column type `SERIAL` to SQLite compatible `INTEGER PRIMARY KEY AUTOINCREMENT`.

### Exact Changes Proposed for `stashies/db.py`
```python
import os
import sqlite3
import logging

logger = logging.getLogger("stashies.db")

class SQLiteConnectionPool:
    """Thread-safe fallback connector mimicking psycopg2 SimpleConnectionPool."""
    def __init__(self, db_path: str):
        self.db_path = db_path

    def getconn(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA foreign_keys=ON;")
            return conn
        except Exception as e:
            logger.error(f"Error opening SQLite connection: {e}")
            raise e

    def putconn(self, conn):
        try:
            if conn:
                conn.close()
        except Exception as e:
            logger.error(f"Error closing SQLite connection: {e}")

class DBManager:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                db_url = "sqlite:///stashstats.db"
            
            # Extract clean file path from sqlite DB URL prefixes
            if db_url.startswith("sqlite:///"):
                db_path = db_url[10:]
            elif db_url.startswith("sqlite://"):
                db_path = db_url[9:]
            else:
                db_path = "stashstats.db"
                
            try:
                cls._pool = SQLiteConnectionPool(db_path)
                logger.info(f"SQLite database pool initialized with path: {db_path}")
                cls.run_migrations()
            except Exception as e:
                logger.error(f"Failed to initialize SQLite database pool: {e}")
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
                logger.info("Database migrations executed successfully.")
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
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
                cur.execute("SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = ?", (stash_id,))
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
                """, (stash_id, yards, meters, skeins, grams))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving original_values for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_stash_history(cls, stash_id: str):
        conn = cls.get_pool().getconn()
        try:
            cur = conn.cursor()
            try:
                cur.execute("SELECT event_date, yards, meters, skeins, grams FROM stash_history WHERE stash_id = ? ORDER BY id ASC", (stash_id,))
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
                """, (stash_id, event_date, yards, meters, skeins, grams))
                conn.commit()
            finally:
                cur.close()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving stash_history event for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)
```

---

## 2. Update `docker-compose.yml`
- **Problem**: Clean up unnecessary Postgres backend service/volumes and prepare mount point for SQLite database.
- **Proposed Solution**: 
  - Remove `db` service definition.
  - Remove `pgdata` volume from the root-level `volumes` list.
  - Define `data` volume for persistent SQLite DB.
  - Remove PostgreSQL environment variables and the `depends_on` service health check for DB from `web` service.
  - Inject updated Ravelry username variable (`RAVELRY_USERNAME`) and sqlite-oriented `DATABASE_URL` under the `web` service.
  - Mount `data:/data` inside the `web` container.
  - Add thread/worker config option in `command` block.

### Exact Changes Proposed for `docker-compose.yml`
Replace lines 1 to 46 of `docker-compose.yml` with:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8050:8050"
    command: gunicorn -b 0.0.0.0:8050 --workers 1 --threads 4 app:server
    environment:
      - API_USERNAME=${API_USERNAME}
      - API_KEY=${API_KEY}
      - RAVELRY_USERNAME=${RAVELRY_USERNAME}
      - DATABASE_URL=sqlite:////data/stashstats.db
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      cache:
        condition: service_started
    volumes:
      - data:/data

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

volumes:
  data:
  redisdata:
```

---

## 3. Update `requirements.txt`
- **Problem**: Strip postgres driver dependencies which could trigger builds failures.
- **Proposed Solution**: Delete line 10 `psycopg2-binary==2.9.6`.

### Exact Changes Proposed for `requirements.txt`
```text
dash==2.11.1
dash-bootstrap-components==1.4.1
pydantic>=2.0.0
pydantic-settings>=2.0.0
requests==2.31.0
python-dotenv==1.0.0
pandas==2.0.2
plotly==5.15.0
redis==4.6.0
gunicorn==20.1.0
```

---

## 4. Update Env Vars & Gunicorn Options
- **Problem**: Ensure execution of dash app runs with 1 worker and 4 threads as requested.
- **Proposed Solution**: Add gunicorn args to both `docker-compose.yml` (done above) and inside the main `Dockerfile` `CMD`.

---

## 5. Replace `USERNAME` with `RAVELRY_USERNAME`
- **Problem**: Prevent using general `USERNAME` env var, switching it to specific Ravelry config setting.
- **Proposed Solution**: Replace `os.getenv("USERNAME")` with `os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")` in all source files, adjust mocks/configurations in test environments, and modify `.env.example`.

### Exact Changes Proposed

#### `stashies/model.py` (Lines 124, 266, 274, 318)
- **Before**: `username = os.getenv("USERNAME") or "Thotsky"`
- **After**: `username = os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")`

#### `tests/test_e2e.py` (Line 12, 55)
- **Before**:
```python
os.environ.setdefault("USERNAME", "test_user")
```
- **After**:
```python
os.environ.setdefault("RAVELRY_USERNAME", "test_user")
```
- **Before**:
```python
        env={**os.environ, "API_USERNAME": "test_user", "API_KEY": "test_key", "USERNAME": "test_user"}
```
- **After**:
```python
        env={**os.environ, "API_USERNAME": "test_user", "API_KEY": "test_key", "RAVELRY_USERNAME": "test_user"}
```

#### `.env.example`
- **Before**:
```ini
USERNAME=YourRavelryUsername
DATABASE_URL=postgresql://stashuser:stashpassword@db:5432/stashstats
```
- **After**:
```ini
RAVELRY_USERNAME=KMLadyBugCrotchets
DATABASE_URL=sqlite:///stashstats.db
```

---

## 6. Lightweight Multi-Stage `Dockerfile`
- **Problem**: Create a small, clean runner container image discarding build/compilation requirements.
- **Proposed Solution**: 
  - Establish a `builder` phase that initiates the python environment and executes pip wheels inside a clean `/opt/venv` virtual env.
  - Establish a `runner` phase that pulls compiled components/packages from the builder, copy codebase files, and specify the production ready gunicorn launch configuration parameters.
  - Drop compile requirements like `gcc` and `libpq-dev` from runner phase.

### Exact Changes Proposed for `Dockerfile`
Replace the entire `Dockerfile` with:
```dockerfile
# Stage 1: Install packages and setup requirements
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Minimal runner container
FROM python:3.11-slim AS runner

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Pull environment libraries from builder phase
COPY --from=builder /opt/venv /opt/venv

# Copy local application code
COPY . .

EXPOSE 8050

# Run with single-worker and 4 threads configuration
CMD ["gunicorn", "-b", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "app:server"]
```

---

## 7. Datepicker for Add to Stash form (`stashies/components/search_results.py`)
- **Problem**: The stash-add form is missing a configuration component specifying the date-added value.
- **Proposed Solution**: Add the `dcc.DatePickerSingle` component to the form layout.

### Exact Changes Proposed for `stashies/components/search_results.py`
Add imports at the top:
```python
import datetime
from dash import dcc
```

Replace lines 138 to 167 (the second dbc.Row structure inside `create_search_result` method) with:
```python
                dbc.Row(
                    [
                        dbc.Col(
                            [
                                dbc.Label("Location"),
                                dbc.Input(
                                    type="text", 
                                    id={"type": "stash-location", "index": id}, 
                                    placeholder="e.g. Closet"
                                ),
                            ],
                            xs=12,
                            sm=4,
                            className="mb-2 mb-sm-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Notes"),
                                dbc.Input(
                                    type="text", 
                                    id={"type": "stash-notes", "index": id}, 
                                    placeholder="e.g. soft texture"
                                ),
                            ],
                            xs=12,
                            sm=4,
                            className="mb-2 mb-sm-0",
                        ),
                        dbc.Col(
                            [
                                dbc.Label("Date Added"),
                                dcc.DatePickerSingle(
                                    id={"type": "stash-date-added", "index": id},
                                    date=datetime.date.today().isoformat(),
                                    display_format="YYYY-MM-DD",
                                    style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"},
                                    className="d-block"
                                ),
                            ],
                            xs=12,
                            sm=4,
                        ),
                    ],
                    className="mb-3",
                ),
```

---

## 8. Datepicker for Log Usage modal tab (`stashies/components/edit_modal.py`)
- **Problem**: The log usage form inside the modal does not capture the date of usage.
- **Proposed Solution**: Add the `dcc.DatePickerSingle` component.

### Exact Changes Proposed for `stashies/components/edit_modal.py`
Add imports at the top:
```python
import datetime
```

Replace lines 159 to 173 (Skeins Used input block in `modal-tab-usage` Tab) with:
```python
                                                        dbc.Label("Skeins Used"),
                                                        dbc.InputGroup(
                                                            [
                                                                dbc.Input(
                                                                    id="edit-stash-used-skeins",
                                                                    type="number",
                                                                    min=0,
                                                                    step=0.25,
                                                                    placeholder="e.g. 1.5",
                                                                    style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"}
                                                                ),
                                                                dbc.InputGroupText("skeins", style={"backgroundColor": "#444", "color": "#ccc", "border": "1px solid #555"}),
                                                            ],
                                                            className="mb-3"
                                                        ),
                                                        dbc.Label("Usage Date"),
                                                        html.Div(
                                                            dcc.DatePickerSingle(
                                                                id="edit-stash-usage-date",
                                                                date=datetime.date.today().isoformat(),
                                                                display_format="YYYY-MM-DD",
                                                                style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"},
                                                                className="d-block"
                                                            ),
                                                            className="mb-3"
                                                        ),
```
