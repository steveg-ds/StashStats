# SPEC: Docker Compose Stack with Postgres & Redis

## §G Goal
Containerize StashStats. Persist delta history/original values in Postgres. Cache Ravelry API responses in Redis.

## §C Context
- Current: single-user local app, cache + history + baseline totals stored in `stash_cache.json` (local file).
- Target: docker compose stack:
  - web: custom python image → runs dash app.
  - db: postgres:15-alpine → stores persistent tables.
  - cache: redis:7-alpine → caches temporary API detail responses.

## §I Interfaces
- DB: PostgreSQL
  - Connection: `DATABASE_URL` env var.
  - Schema:
    ```sql
    CREATE TABLE IF NOT EXISTS original_values (
        stash_id VARCHAR(50) PRIMARY KEY,
        yards DOUBLE PRECISION NOT NULL,
        meters DOUBLE PRECISION NOT NULL,
        skeins DOUBLE PRECISION NOT NULL,
        grams DOUBLE PRECISION NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

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
    CREATE INDEX IF NOT EXISTS idx_history_stash_id ON stash_history(stash_id);
    ```

- Cache: Redis
  - Connection: `REDIS_URL` env var.
  - Key: `stash_detail:<stash_id>` → JSON string: `{"updated_at": "...", "packs": [...]}`
  - TTL: 86400 (24h).

- Environment variables (`.env` & `docker-compose.yml`):
  - `API_USERNAME`, `API_KEY`, `USERNAME` (Ravelry creds)
  - `DATABASE_URL` (e.g. `postgresql://stashuser:stashpassword@db:5432/stashstats`)
  - `REDIS_URL` (e.g. `redis://cache:6379/0`)

## §V Invariants
- V1: get_stash_list → check redis cache. `updated_at` match → return cache details.
- V2: cache miss OR `updated_at` mismatch → fetch Ravelry detail → store in redis & compare totals.
- V3: delta totals ≠ 0 → save event in postgres `stash_history`.
- V4: original totals not in DB → save baseline in postgres `original_values`.
- V5: update_stash → delete redis cache key `stash_detail:<stash_id>`.

## §T Tasks
id|status|task|cites
---|---|---|---
T1|.|add `redis`, `psycopg2-binary` to dependencies|
T2|.|create Dockerfile & docker-compose.yml|
T3|.|implement db manager / table migrations in `stashies/db.py`|
T4|.|integrate database & redis cache into `stashies/model.py`|
T5|.|update `.gitignore` & add default `.env.example`|
T6|.|run tests & verify docker-compose stack starts|

## §B Bugs
id|date|cause|fix
---|---|---|---
