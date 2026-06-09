# Docker Compose Stack with Postgres & Redis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run StashStats application in docker-compose stack with custom image, Redis for caching, and PostgreSQL for lightweight SQL persistence.

**Architecture:** Split existing JSON cache (`stash_cache.json`): volatile details cached in Redis, delta history & baseline original values persisted in PostgreSQL database. Docker Compose coordinates Dash web server, PostgreSQL database, and Redis cache.

**Tech Stack:** Python 3.11, Dash, Redis (python-redis), PostgreSQL (psycopg2-binary), Docker, Docker Compose

---

### Task 1: Project Metadata & Package Configuration

**Files:**
- Create: `requirements.txt`
- Modify: `.gitignore`
- Create: `.env.example`

- [ ] **Step 1: Create requirements.txt**
Create `/home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/requirements.txt` with python package dependencies:
```txt
dash==2.11.1
dash-bootstrap-components==1.4.1
pydantic==1.10.9
pydantic-settings==2.0.2
requests==2.31.0
python-dotenv==1.0.0
pandas==2.0.2
plotly==5.15.0
redis==4.6.0
psycopg2-binary==2.9.6
gunicorn==20.1.0
```

- [ ] **Step 2: Update .gitignore**
Modify `/home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/.gitignore` to ignore local cache file, logs, and environments:
```gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
.venv/
venv/
ENV/
env/

# IDEs
.idea/
.vscode/

# Project Cache & Logs
stash_cache.json
dev_changes.log
.env
data/
```

- [ ] **Step 3: Create .env.example**
Create `/home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/.env.example`:
```env
# Ravelry API Credentials
API_USERNAME=your_personal_access_username
API_KEY=your_personal_access_password
USERNAME=YourRavelryUsername

# Local dev/docker environment variables
DATABASE_URL=postgresql://stashuser:stashpassword@db:5432/stashstats
REDIS_URL=redis://cache:6379/0
```

- [ ] **Step 4: Commit dependencies**
```bash
git add requirements.txt .gitignore .env.example
git commit -m "chore: configure package dependencies, gitignore, and env example"
```

---

### Task 2: Docker Setup (Dockerfile & docker-compose.yml)

**Files:**
- Create: `Dockerfile`
- Create: `docker-compose.yml`

- [ ] **Step 1: Create Dockerfile**
Create `/home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/Dockerfile` using lightweight python base:
```dockerfile
FROM python:3.11-slim

# Prevent writing pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

# Install system dependencies needed for psycopg2 compilation if needed (slim image might need libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Expose port
EXPOSE 8050

# Run with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8050", "app:app"]
```

- [ ] **Step 2: Create docker-compose.yml**
Create `/home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/docker-compose.yml`:
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
      - USERNAME=${USERNAME}
      - DATABASE_URL=postgresql://stashuser:stashpassword@db:5432/stashstats
      - REDIS_URL=redis://cache:6379/0
    depends_on:
      db:
        condition: service_healthy
      cache:
        condition: service_started

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=stashuser
      - POSTGRES_PASSWORD=stashpassword
      - POSTGRES_DB=stashstats
    volumes:
      - pgdata:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U stashuser -d stashstats"]
      interval: 5s
      timeout: 5s
      retries: 5

  cache:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

- [ ] **Step 3: Commit Docker configuration**
```bash
git add Dockerfile docker-compose.yml
git commit -m "feat: add Dockerfile and docker-compose.yml stack configuration"
```

---

### Task 3: Database Manager & Migrations

**Files:**
- Create: `stashies/db.py`

- [ ] **Step 1: Write DB Manager code**
Create `/home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/db.py` to handle postgres connectivity, table creation, and baseline/history CRUD:
```python
import os
import logging
import psycopg2
from psycopg2 import pool

logger = logging.getLogger("stashies.db")

class DBManager:
    _pool = None

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            db_url = os.getenv("DATABASE_URL")
            if not db_url:
                # Fallback to local postgres if DATABASE_URL is not set (e.g. during local tests)
                db_url = "postgresql://stashuser:stashpassword@localhost:5432/stashstats"
            try:
                cls._pool = psycopg2.pool.SimpleConnectionPool(1, 10, dsn=db_url)
                logger.info("Database connection pool initialized.")
                cls.run_migrations()
            except Exception as e:
                logger.error(f"Failed to initialize database connection pool: {e}")
                raise e
        return cls._pool

    @classmethod
    def run_migrations(cls):
        conn = cls.get_pool().getconn()
        try:
            with conn.cursor() as cur:
                cur.execute("""
                CREATE TABLE IF NOT EXISTS original_values (
                    stash_id VARCHAR(50) PRIMARY KEY,
                    yards DOUBLE PRECISION NOT NULL,
                    meters DOUBLE PRECISION NOT NULL,
                    skeins DOUBLE PRECISION NOT NULL,
                    grams DOUBLE PRECISION NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """)
                cur.execute("""
                CREATE TABLE IF NOT EXISTS stash_history (
                    id SERIAL PRIMARY KEY,
                    stash_id VARCHAR(50) NOT NULL,
                    event_date VARCHAR(20) NOT NULL,
                    yards DOUBLE PRECISION NOT NULL,
                    meters DOUBLE PRECISION NOT NULL,
                    skeins DOUBLE PRECISION NOT NULL,
                    grams DOUBLE PRECISION NOT NULL,
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
                cur.execute("SELECT yards, meters, skeins, grams FROM original_values WHERE stash_id = %s", (stash_id,))
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
                VALUES (%s, %s, %s, %s, %s)
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
                cur.execute("SELECT event_date, yards, meters, skeins, grams FROM stash_history WHERE stash_id = %s ORDER BY id ASC", (stash_id,))
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
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (stash_id, event_date, yards, meters, skeins, grams))
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error saving stash_history event for stash {stash_id}: {e}")
        finally:
            cls.get_pool().putconn(conn)
```

- [ ] **Step 2: Commit DB Manager**
```bash
git add stashies/db.py
git commit -m "feat: implement DBManager helper for PostgreSQL storage & migration"
```

---

### Task 4: Integrate Redis & PostgreSQL in Model Layer

**Files:**
- Modify: `stashies/model.py`

- [ ] **Step 1: Replace stash_cache.json with Redis and Postgres in model.py**
Modify `/home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/model.py` to:
1. Initialize Redis connection client.
2. Initialize Postgres pool (lazily via DBManager).
3. Update `get_stash_list` to check Redis cache for detailed stash entries (with TTL check), fetch DBManager for history & original_values.
4. Update `update_stash` to delete key from Redis.

Here is the exact code to replace starting at `class Model(Base):`:
```python
@dataclass
class Model(Base):
    """
    MVC Model layer — wraps Ravelry API calls and local cache management.

    - Properties:
        - REQ (Req): Authenticated HTTP client for Ravelry API.
    """
    REQ: 'Req' = Field(default_factory=Req)
    _redis: Any = None

    def get_redis(self):
        if self._redis is None:
            import redis
            redis_url = os.getenv("REDIS_URL")
            if not redis_url:
                redis_url = "redis://localhost:6379/0"
            try:
                self._redis = redis.Redis.from_url(redis_url, decode_responses=True)
            except Exception as e:
                self.LOGGER.error(f"Redis initialization failed: {e}")
        return self._redis

    def search_yarn(
        self,
        query: str,
        sort: str = "best",
        page_size: int = 10,
    ) -> Union[List['Yarn'], None]:
        """
        Search Ravelry yarn database by keyword.
        """
        params = {"query": query, "page": 1, "page_size": page_size, "sort": sort}

        data: Optional[Dict[str, Any]] = self.REQ.get_request(
            endpoint="yarns/search.json", params=params
        )

        if data is not None:
            yarns_data = data.get('yarns')
            if not yarns_data:
                return None
            yarns = [Yarn(**yarn) for yarn in yarns_data]
            return yarns
        return None

    def get_stash_list(self) -> Optional[List[Dict[str, Any]]]:
        """
        Fetch all stash entries for the configured user, enriched with pack details.
        """
        import os
        import json
        import concurrent.futures
        from .db import DBManager
        
        username = os.getenv("USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/list.json"
        
        all_stashes = []
        page = 1
        while True:
            result = self.REQ.get_request(
                endpoint=endpoint, 
                params={"page_size": 100, "page": page}
            )
            if not result or "stash" not in result or not result["stash"]:
                break
            all_stashes.extend(result["stash"])
            if len(result["stash"]) < 100:
                break
            page += 1
            
        if not all_stashes:
            return None
            
        # Ensure DB tables exist
        DBManager.get_pool()

        # Connect to Redis
        r = self.get_redis()

        dirty_items = []
        for s in all_stashes:
            if "id" not in s:
                continue
            stash_id = str(s["id"])
            updated_at = s.get("updated_at")
            
            # Read from Redis cache
            cached_val = None
            if r:
                try:
                    cached_val = r.get(f"stash_detail:{stash_id}")
                except Exception as e:
                    self.LOGGER.error(f"Redis get failed: {e}")

            if cached_val:
                try:
                    cached_data = json.loads(cached_val)
                    if cached_data.get("updated_at") == updated_at:
                        s["packs"] = cached_data.get("packs") or []
                        # Retrieve history and original_values from PostgreSQL
                        s["history"] = DBManager.get_stash_history(stash_id) or []
                        s["original_values"] = DBManager.get_original_values(stash_id)
                        continue
                except Exception as e:
                    self.LOGGER.error(f"Failed to parse cached details for {stash_id}: {e}")

            dirty_items.append(s)
                
        if dirty_items:
            def fetch_detail(item):
                import time
                s_id = item.get("id")
                if not s_id:
                    return None, None
                time.sleep(0.2)  # rate limit compliance
                detail_endpoint = f"people/{username}/stash/{s_id}.json"
                try:
                    res = self.REQ.get_request(detail_endpoint)
                    if res and "stash" in res:
                        return s_id, res["stash"]
                except Exception as e:
                    self.LOGGER.error(f"Error fetching stash detail {s_id}: {e}")
                return s_id, None
                
            max_workers = min(3, len(dirty_items))
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                results = list(executor.map(fetch_detail, dirty_items))
                
            for s_id, stash_detail in results:
                if stash_detail:
                    s_id_str = str(s_id)
                    new_packs = stash_detail.get("packs") or []
                    yarn_info = stash_detail.get("yarn") or {}
                    new_totals = get_primary_totals(new_packs, yarn_info)
                    
                    old_totals = DBManager.get_original_values(s_id_str)
                    
                    if old_totals:
                        delta = {
                            "yards": new_totals["yards"] - old_totals["yards"],
                            "meters": new_totals["meters"] - old_totals["meters"],
                            "skeins": new_totals["skeins"] - old_totals["skeins"],
                            "grams": new_totals["grams"] - old_totals["grams"]
                        }
                        
                        # Only record a history event when pack totals actually changed
                        if any(val != 0.0 for val in delta.values()):
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
                    else:
                        # Baseline first-seen original_values
                        DBManager.save_original_values(
                            stash_id=s_id_str,
                            yards=new_totals["yards"],
                            meters=new_totals["meters"],
                            skeins=new_totals["skeins"],
                            grams=new_totals["grams"]
                        )
                    
                    # Store details in Redis with 24 hour TTL
                    if r:
                        try:
                            r.setex(
                                f"stash_detail:{s_id_str}",
                                86400,
                                json.dumps({
                                    "updated_at": stash_detail.get("updated_at"),
                                    "packs": new_packs
                                })
                            )
                        except Exception as e:
                            self.LOGGER.error(f"Redis set failed for {s_id_str}: {e}")

                    for item in all_stashes:
                        if item["id"] == s_id:
                            item["packs"] = new_packs
                            item["history"] = DBManager.get_stash_history(s_id_str) or []
                            item["original_values"] = DBManager.get_original_values(s_id_str)
                            break
                            
        return all_stashes

    def create_stash(self, stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Post a new stash entry to the user's Ravelry stash.
        """
        import os
        username = os.getenv("USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/create.json"
        return self.REQ.post_request(endpoint=endpoint, data=stash_data)

    def update_stash(self, stash_id: Union[str, int], stash_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a stash entry via PUT and invalidate local cache for that entry."""
        import os

        username = os.getenv("USERNAME") or "Thotsky"
        endpoint = f"people/{username}/stash/{stash_id}.json"
        result = self.REQ.put_request(endpoint=endpoint, data=stash_data)

        # Invalidate Redis cache
        r = self.get_redis()
        if r:
            try:
                r.delete(f"stash_detail:{stash_id}")
            except Exception as e:
                self.LOGGER.error(f"Cache invalidation failed for stash {stash_id} in Redis: {e}")

        return result
```

- [ ] **Step 2: Commit model changes**
```bash
git add stashies/model.py
git commit -m "feat: integrate Redis caching and PostgreSQL persistence in Model layer"
```

---

### Task 5: Setup Tests & Mocking for local tests

**Files:**
- Modify: `tests/test_e2e.py`

- [ ] **Step 1: Mock Redis and Postgres connection in test suite**
Modify `tests/test_e2e.py` to patch `redis` client and `psycopg2` calls, or mock `DBManager` & `Model.get_redis` to avoid requiring external Redis/Postgres services for local pytest runs.
Add this block at the top of `tests/test_e2e.py` (after imports) to mock PostgreSQL and Redis:
```python
from unittest.mock import MagicMock
import sys

# Mock DBManager & Redis globally in test runner
class MockDBManager:
    _history = {}
    _orig = {}

    @classmethod
    def get_pool(cls):
        return MagicMock()

    @classmethod
    def get_original_values(cls, stash_id):
        return cls._orig.get(stash_id)

    @classmethod
    def save_original_values(cls, stash_id, yards, meters, skeins, grams):
        cls._orig[stash_id] = {"yards": yards, "meters": meters, "skeins": skeins, "grams": grams}

    @classmethod
    def get_stash_history(cls, stash_id):
        return cls._history.get(stash_id, [])

    @classmethod
    def save_history_event(cls, stash_id, event_date, yards, meters, skeins, grams):
        cls._history.setdefault(stash_id, []).append({
            "date": event_date, "yards": yards, "meters": meters, "skeins": skeins, "grams": grams
        })

# Apply mocks to test environment before import
import stashies.db
stashies.db.DBManager = MockDBManager

# Mock redis module
sys.modules['redis'] = MagicMock()
```

- [ ] **Step 2: Run pytest locally**
Run: `pytest tests/test_e2e.py -v`
Expected: Tests pass with mocking.

- [ ] **Step 3: Commit test modifications**
```bash
git add tests/test_e2e.py
git commit -m "test: mock database and cache services in test suite for offline testing"
```

---

### Task 6: Build Stack and Verify Docker Compose

- [ ] **Step 1: Verify Stack builds locally**
Run: `docker compose build`
Expected: Custom image builds successfully.

- [ ] **Step 2: Run docker compose stack**
Run: `docker compose up -d`
Expected: 3 containers start up and run.

- [ ] **Step 3: Check docker compose logs**
Run: `docker compose logs`
Expected: No fatal db/cache connection errors.

- [ ] **Step 4: Cleanup stack**
Run: `docker compose down -v`
Expected: Containers and volumes removed.

---
