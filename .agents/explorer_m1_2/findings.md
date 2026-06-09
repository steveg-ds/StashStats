# Findings Report — SQLite Migration & UI Updates

This findings report details the implementation strategy and exact code modifications required to migrate the database from PostgreSQL to SQLite, update environmental/Docker configuration, fix username handling, implement a lightweight two-stage Dockerfile, and add date pickers to the Dash app interface.

---

## 1. Replace PostgreSQL with SQLite (`stashies/db.py`)

### Code Structure & Current State
The database manager `stashies/db.py` relies on `psycopg2` and `SimpleConnectionPool` to manage PostgreSQL connections. It uses `%s` placeholders for queries, which are incompatible with SQLite.

### Proposed Changes
1. **Remove `psycopg2` Imports**: Replace them with Python's standard library `sqlite3`.
2. **Implement `SQLiteConnectionPool`**: Define a compatibility class that implements `getconn()` and `putconn(conn)` to avoid modifying connection lifecycle calls elsewhere.
3. **Connection parameters**: Enable WAL journal mode (`PRAGMA journal_mode=WAL`) on connection retrieval and set `check_same_thread=False`.
4. **Update Schema & Syntax**: Replace `%s` placeholders with `?`. Modify the Postgres `SERIAL PRIMARY KEY` to SQLite's `INTEGER PRIMARY KEY AUTOINCREMENT`. Replace postgres-specific type names (`DOUBLE PRECISION`, `VARCHAR`) with SQLite-friendly types (`REAL`, `TEXT`).
5. **Database Path**: Load from environment variable `SQLITE_DB_PATH` with a fallback to `/app/data/stash.db`.

### Exact Code Changes to `stashies/db.py`
```python
import os
import logging
import sqlite3

logger = logging.getLogger("stashies.db")

class SQLiteCursor(sqlite3.Cursor):
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class SQLiteConnection(sqlite3.Connection):
    def cursor(self, *args, **kwargs):
        return super().cursor(factory=SQLiteCursor)

class SQLiteConnectionPool:
    def __init__(self, db_path: str):
        self.db_path = db_path
        # Ensure parent directory exists
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)

    def getconn(self):
        conn = sqlite3.connect(self.db_path, factory=SQLiteConnection, check_same_thread=False)
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def putconn(self, conn):
        conn.close()

class DBManager:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            db_path = os.getenv("SQLITE_DB_PATH", "/app/data/stash.db")
            try:
                cls._pool = SQLiteConnectionPool(db_path)
                logger.info(f"SQLite database pool initialized at {db_path}.")
                cls.run_migrations()
            except Exception as e:
                logger.error(f"Failed to initialize SQLite database: {e}")
                raise e
        return cls._pool

    @classmethod
    def run_migrations(cls):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
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
            with conn.cursor() as cur:
                cur.execute("SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = ?", (stash_id,))
                row = cur.fetchone()
                if row:
                    return {"yards": row[0], "meters": row[1], "skeins": row[2], "grams": row[3]}
                return None
        except Exception as e:
            logger.error(f"Error reading original_values for stash {stash_id}: {e}")
            return None
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_original_values(cls, stash_id: str, yards: float, meters: float, skeins: float, grams: float):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO original_values (stash_id, yards, meters, skeins, grams)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT (stash_id) DO NOTHING
                """, (stash_id, yards, meters, skeins, grams))
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving original_values for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def get_stash_history(cls, stash_id: str):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
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
        except Exception as e:
            logger.error(f"Error reading stash_history for stash {stash_id}: {e}")
            return []
        finally:
            cls.get_pool().putconn(conn)

    @classmethod
    def save_history_event(cls, stash_id: str, event_date: str, yards: float, meters: float, skeins: float, grams: float):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO stash_history (stash_id, event_date, yards, meters, skeins, grams)
                VALUES (?, ?, ?, ?, ?, ?)
                """, (stash_id, event_date, yards, meters, skeins, grams))
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving stash_history event for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)
```

---

## 2. Update `docker-compose.yml`

### Code Structure & Current State
The existing configuration sets up three services (`web`, `db`, and `cache`), uses the `pgdata` volume, and passes postgres connection settings to `web`.

### Proposed Changes
1. Remove the `db` service definition.
2. Remove the `pgdata` volume block under `volumes`.
3. Add a local directory bind mount (`./data:/app/data`) to the `web` service to persist SQLite database storage.
4. Remove the `DATABASE_URL` environment variable from the `web` service environment list.
5. Add `SQLITE_DB_PATH=/app/data/stash.db` to the `web` service environment list.
6. Replace `USERNAME=${USERNAME}` with `RAVELRY_USERNAME=${RAVELRY_USERNAME}`.
7. Simplify `depends_on` under the `web` service, removing the postgres healthcheck dependency.

### Exact Code Changes to `docker-compose.yml`
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
      - cache
    command: ["gunicorn", "-b", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "app:server"]

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

## 3. Update `requirements.txt`

### Code Structure & Current State
Includes `psycopg2-binary==2.9.6` on line 10.

### Proposed Changes
Delete line 10 to remove compile and runtime postgres dependency.

### Exact Code Changes to `requirements.txt`
```diff
--- requirements.txt
+++ requirements.txt
@@ -7,4 +7,3 @@
 pandas==2.0.2
 plotly==5.15.0
 redis==4.6.0
-psycopg2-binary==2.9.6
 gunicorn==20.1.0
```

---

## 4. Update Gunicorn CMD Settings & Environment Variables

### Code Structure & Current State
The single-stage `Dockerfile` uses standard `gunicorn -b 0.0.0.0:8050 app:server` (no workers or threads settings, which defaults to 1 worker and 1 thread). SQLite requires single-write access to avoid locking; multi-threading is handled cleanly using `--workers 1 --threads 4`.

### Proposed Changes
Update the CMD block of the Dockerfile to specify workers and threads parameters, and mirror it in the `docker-compose.yml` command option.

### Exact CMD Update:
```dockerfile
CMD ["gunicorn", "-b", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "app:server"]
```

---

## 5. Fix USERNAME Environment Variable

### Code Structure & Current State
`stashies/model.py` and `tests/test_e2e.py` reference `os.getenv("USERNAME")`. In Linux, the shell injects `USERNAME` automatically with the current system login username (e.g. `thotsky`), overriding container configs.

### Proposed Changes
Replace all references to `os.getenv("USERNAME")` with `os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")`. Pass `RAVELRY_USERNAME` in `docker-compose.yml` and define it in `.env.example`.

### Exact Code Changes to `stashies/model.py`
Update lines 124, 266, 274, and 318:
```python
# Replace
username = os.getenv("USERNAME") or "Thotsky"
# With
username = os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")
```

### Exact Code Changes to `tests/test_e2e.py`
Update lines 12 and 55:
```python
# In tests/test_e2e.py:12
# Replace
os.environ.setdefault("USERNAME", "test_user")
# With
os.environ.setdefault("RAVELRY_USERNAME", "test_user")

# In tests/test_e2e.py:55
# Replace
    proc = subprocess.Popen(
        [".venv/bin/python", "app.py"],
        env={**os.environ, "API_USERNAME": "test_user", "API_KEY": "test_key", "USERNAME": "test_user"}
    )
# With
    proc = subprocess.Popen(
        [".venv/bin/python", "app.py"],
        env={**os.environ, "API_USERNAME": "test_user", "API_KEY": "test_key", "RAVELRY_USERNAME": "test_user"}
    )
```

### Exact Code Changes to `.env.example`
```diff
--- .env.example
+++ .env.example
@@ -1,8 +1,8 @@
 # Ravelry API Credentials
 API_USERNAME=your_personal_access_username
 API_KEY=your_personal_access_password
-USERNAME=YourRavelryUsername
+RAVELRY_USERNAME=YourRavelryUsername
 
 # Local dev/docker environment variables
-DATABASE_URL=postgresql://stashuser:stashpassword@db:5432/stashstats
 REDIS_URL=redis://cache:6379/0
+SQLITE_DB_PATH=/app/data/stash.db
```

---

## 6. Lightweight Multi-Stage Dockerfile

### Code Structure & Current State
The existing `Dockerfile` executes a single stage that compiles/installs tools like `gcc` and `libpq-dev` which remain in the final image.

### Proposed Changes
Implement a two-stage build.
1. **Stage 1 (Builder)**: Setup system dependencies and build libraries inside a temporary build container. Create and install requirements into a Python virtual environment `/opt/venv`.
2. **Stage 2 (Runtime)**: Copy only the built virtual environment (`/opt/venv`) and codebase into a clean, minimal `python:3.11-slim` runtime container. Exclude build-essential tools (`gcc`, compilation artifacts) to reduce final size.

### Exact Code Changes to `Dockerfile`
```dockerfile
# Stage 1: Build virtual environment
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install compilation tools (in case any packages require binary building)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

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

COPY --from=builder /opt/venv /opt/venv
COPY . .

EXPOSE 8050

CMD ["gunicorn", "-b", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "app:server"]
```

---

## 7. DatePickerSingle in `stashies/components/search_results.py`

### Code Structure & Current State
The search result component builds an inline "Add to Stash" form but lacks a date input.

### Proposed Changes
1. Import `datetime` and `dcc` at the top of the file.
2. Insert `DatePickerSingle` with ID pattern `{"type": "stash-date-added", "index": id}` inside `stash_form` after the Location/Notes row.

### Exact Code Changes to `stashies/components/search_results.py`
```diff
--- stashies/components/search_results.py
+++ stashies/components/search_results.py
@@ -1,8 +1,9 @@
 """Dash component for rendering yarn search results as an accordion with inline stash-add forms."""
+import datetime
 import dash_bootstrap_components as dbc
-from dash import html
+from dash import html, dcc
 from pydantic.dataclasses import dataclass
 from pydantic import Field, HttpUrl
 from typing import Dict, Any, Optional, List
@@ -166,6 +167,23 @@
                     ],
                     className="mb-3",
                 ),
+                dbc.Row(
+                    [
+                        dbc.Col(
+                            [
+                                dbc.Label("Date Added"),
+                                html.Br(),
+                                dcc.DatePickerSingle(
+                                    id={"type": "stash-date-added", "index": id},
+                                    date=datetime.date.today().isoformat(),
+                                    display_format="YYYY-MM-DD",
+                                    className="w-100"
+                                ),
+                            ],
+                            xs=12,
+                        )
+                    ],
+                    className="mb-3"
+                ),
                 dbc.Button(
                     "Add Yarn to Stash", 
                     id={"type": "stash-submit-btn", "index": id},
```

---

## 8. DatePickerSingle in `stashies/components/edit_modal.py`

### Code Structure & Current State
The Log Usage modal has a "Skeins Used" input field but lacks a date usage input field.

### Proposed Changes
1. Import `datetime` at the top of the file.
2. Insert `DatePickerSingle` with ID `"edit-stash-usage-date"` in the Log Usage tab below the "Skeins Used" input group.

### Exact Code Changes to `stashies/components/edit_modal.py`
```diff
--- stashies/components/edit_modal.py
+++ stashies/components/edit_modal.py
@@ -1,5 +1,6 @@
 """Dash component for the edit stash modal."""
+import datetime
 from typing import Any, ClassVar, Dict, List
 import dash_bootstrap_components as dbc
-from dash import dcc, html
+from dash import dcc, html
 from pydantic.dataclasses import dataclass
@@ -172,6 +173,18 @@
                                                             className="mb-3"
                                                         ),
+                                                        dbc.Label("Date Used"),
+                                                        html.Br(),
+                                                        dcc.DatePickerSingle(
+                                                            id="edit-stash-usage-date",
+                                                            date=datetime.date.today().isoformat(),
+                                                            display_format="YYYY-MM-DD",
+                                                            style={"backgroundColor": "#333", "color": "#fff", "border": "1px solid #555"},
+                                                            className="w-100 mb-3"
+                                                        ),
                                                         html.Div(
                                                             id="edit-stash-remaining-preview",
                                                             className="mt-2 p-3 rounded",
```
