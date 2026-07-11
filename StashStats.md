---
aliases: []
tags: []
---

# StashStats

Dash-based web app. Search, track, manage personal yarn stash via Ravelry API.

---

## TODOs

- [x] log usage modal has past changes table below buttons
- [x] remove Needles, Hooks, Queue tabs
- [x] fix stash card photo rendering
- [x] dev + prod Docker Compose stack
- [ ] \#TODO there has to be some way to clean up this list at least the completed tasks
- [x] \#TODO add logging. so much logging. -> reduced logging to WARNING to resolve performance issues
- [x] #TODO editing colorway names in edit modal still broken. other inputs possibly still broken
- [ ] \#TODO

### 🔴 Critical

- [x] `Optional`/`List` missing import in `search_results.py:21`. Fixed.
- [x] `data['yarns']` key guard missing in `model.py:75`. Fixed.
- [x] `USERNAME` collision with OS env. Renamed to `RAVELRY_USERNAME`.
- [x] `MagicMock` import order in `tests/test_e2e.py`. Fixed.

### 🟡 Warnings

- [x] Edit modal missing yarn name. Fixed.
- [x] First stash card auto-opens edit modal on load. Fixed.
- [x] Stash list doesn't auto-refresh after edit. (Note: fixed via trigger callbacks).
- [x] Subtraction loop double counts child packs in `app.py`. Fixed.
- [x] `search-category` State ignored in `app.py`. Fixed.
- [x] `search-sort` best\_match mismatch with best API. Fixed.
- [ ] Project fetch not paginated (>100 projects missed).
- [x] Stale packs left in cache on invalidation. Fixed by Redis delete.
- [ ] ThreadPoolExecutor sleep rate-limiting concurrent burst.
- [x] `stash_cache.json` non-atomic writes. (Obsolete, migrated to Redis/DB).
- [x] `stash_cache.json` relative path. (Obsolete).
- [x] `stash_cache.json` unbound growth. (Obsolete).
- [ ] `stash_post.py` schemas unused in create path.
- [ ] `memory-output` dead Store component.
- [ ] `btn_ids` ordering assumption in `app.py`.
- [ ] `payload` partial pack update contract check.
- [ ] History event bare key access crashes on malformed data.
- [x] `yarn.py` name key guard. Fixed.
- [x] `dash_server` test fixture strips PATH env. (Obsolete, using thread-based fixture).
- [x] `test_stash_yarn_flow` E2E test body empty. Fixed.

### 🔵 Minor

- [x] `sorted(set(…))` unordered set fix.
- [ ] `random.choice(v)` photo selection non-deterministic.
- [x] `dev_changes.log` always-on without gate. Fixed.
- [x] Yards-to-meters constant duplication. Fixed.
- [ ] Redundant `len` checks in `app.py`.
- [ ] Flaky test sleep times.
- [x] Test cache cleanup between runs. (Obsolete, no local cache file used).
- [ ] Lack of tests for write path.

---

## Potential Improvements / Feature Ideas

### UX / UI

- **Stash list sorting** — (Note: Brand, Name, Qty, Date sorting added).
- [x] **Stash list pagination** — added server-side pagination (10 groups/page).
- **Stash list grouping** — group by fiber, weight, location.
- **Stash detail view** — card click detail overlay.
- **Bulk status update** — multi-select updates.
- **Yarn weight/fiber filter** — categories selection filter.
- **Search by colorway within stash**.
- **Photo carousel** for multi-photo yarns.

### Analytics

- **Acquisition rate chart**.
- **Consumption vs acquisition** net growth chart.
- **Project timeline overlay**.
- **Stash age heatmap**.

### Data / Backend

- **Redis caching** — implemented.
- **Cache warm-up** on app startup.
- **Ravelry OAuth** for multi-user.
- **`update_stash`** **validation** schema.
- **DELETE stash entry** UI integration.
- **PATCH yards\_per\_skein** override.
- **Export to CSV/JSON** downloads.
- **Import from CSV** uploads.

### Testing

- Unit tests for analytics dataframe logic.
- Edit modal population tests.
- Stash write path mock tests.
- Log usage math boundary tests.
- Playwright E2E tests for stash tab.
- Concurrent cache write tests.

### Ops / Dev

- Gate `dev_changes.log` with `DEV_LOGGING` env var.
- Gitignore cache and logs.
- Python path package installation config.
- Pinned requirements versions.
- Health check endpoints.

---

## Setup and Running

### 1. Virtual Environment

```bash
python3 -m venv .venv
.venv/bin/pip install dash dash-bootstrap-components pydantic pydantic-settings \
    requests python-dotenv playwright pytest pytest-playwright pandas plotly
```

### 2. Environment Variables

Create `.env` in project root:

```env
# Ravelry API — use "Basic Auth, personal" credentials for write access
API_USERNAME=your_personal_access_username
API_KEY=your_personal_access_password

# Your Ravelry profile username
USERNAME=YourRavelryUsername

# Optional: OAuth credentials (for future multi-user support)
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
REDIRECT_URI=https://your-domain/callback
```

> **Note:** The read-only Basic Auth credentials (`read-…`) will cause 403 on all write operations (edit, log usage, add to stash). Use the **personal** credentials.

### 3. Start Application

```bash
PYTHONPATH=. .venv/bin/python app.py
```

App runs at <http://127.0.0.1:8050>

For dev with auto-restart on crash:

```bash
while true; do PYTHONPATH=. .venv/bin/python app.py; sleep 1; done
```

### 4. Watch Dev Write Log

```bash
tail -f dev_changes.log
```

---

## Automated Testing

E2E tests use Playwright + a thread-hosted Dash server. API calls are mocked inside the test process (same thread, so patches work).

```bash
# Install Playwright browsers first (one-time)
.venv/bin/playwright install chromium

# Run tests
PYTHONPATH=. .venv/bin/pytest tests/test_e2e.py -v
```

Tests currently cover:

- Yarn search → expand result → fill stash form → add to stash → verify success message
- Stash Analytics tab load → Plotly graph rendered → title present
- `_get_primary_totals()` unit test (primary vs child pack separation)

---

## File Index

| File                                    | Purpose                                                              |
| --------------------------------------- | -------------------------------------------------------------------- |
| `app.py`                                | Dash app + all callbacks (search, stash list, analytics, edit modal) |
| `stashies/app_controller.py`            | Tab layout + search result rendering                                 |
| `stashies/model.py`                     | All Ravelry API calls + cache logic                                  |
| `stashies/base_req.py`                  | Raw HTTP GET/POST/PUT with Basic Auth                                |
| `stashies/base.py`                      | Logger injection base class                                          |
| `stashies/components/search.py`         | Search bar UI component                                              |
| `stashies/components/search_results.py` | Search result card + add-to-stash form                               |
| `stashies/components/header.py`         | Logo header                                                          |
| `stashies/dataclasses/yarn.py`          | Pydantic Yarn validation schema                                      |
| `stashies/dataclasses/yarn_photos.py`   | Photo URL container with fallback                                    |
| `stashies/dataclasses/stash_post.py`    | StashPost/PackPost schema (unused in create path)                    |
| `stashies/utils/logger_func.py`         | Logger factory with optional file handler                            |
| `stashies/utils/model_config.py`        | Shared Pydantic config                                               |
| `stash_cache.json`                      | Local stash detail cache (do not commit)                             |
| `dev_changes.log`                       | Write audit log for dev (do not commit)                              |
| `tests/test_e2e.py`                     | Playwright E2E + unit tests                                          |
| `Stash Object Analysis.md`              | Ravelry stash API response field reference                           |
| `stash_stats_code_review.md`            | Previous OAuth implementation code review                            |

# Ravelry Notes

!\[\[NotebookLM Mind Map.png]]

- \[\[Platform Features]]
  - \[\[Pattern Data]]
    - \[\[Search and Metadata]]
    - \[\[Categories and Attributes]]
    - \[\[Designer Information]]
    - \[\[Pattern Sources]]
  - \[\[Yarn Database]]
    - \[\[Weight and Thickness]]
    - \[\[Fiber Composition]]
    - \[\[Color Families]]
    - \[\[Brands and Shops]]
  - \[\[User Content]]
    - \[\[Personal Notebook]]
    - \[\[Project Tracking]]
    - \[\[Yarn Stash]]
    - \[\[Queue and Favorites]]
  - \[\[Authentication]]
    - \[\[Ravelry Basic HTTP Auth|Basic HTTP Auth]]
    - \[\[Ravelry OAuth 2.0|OAuth 2.0]]
    - \[\[Ravelry Security and Setup|Security & Setup]]
  - \[\[SDKs and Libraries]]
    - \[\[ravelRy]]
      - \[\[Ravelry search\_patterns Function|search\_patterns()]]
      - \[\[Ravelry get\_yarns Function|get\_yarns()]]
      - \[\[Ravelry ravelry\_auth Function|ravelry\_auth()]]
    - \[\[Ravelry Python Ecosystem|Python Ecosystem]]
      - \[\[Ravelry Knotion Library|Knotion library]]
      - \[\[Ravelry Flask-FastAPI Integration|Flask/FastAPI Integration]]
      - \[\[Ravelry Reticulate Bridge|Reticulate Bridge]]
    - \[\[Ravelry PHP and Go|PHP & Go]]
    - \[\[Ravelry Kotlin and Android|Kotlin & Android]]
  - \[\[Ravelry Mobile Ecosystem|Mobile Ecosystem]]
  - \[\[Ravelry Technical Architecture|Technical Architecture]]
    - \[\[Ravelry Endpoint Design|Endpoint Design]]
    - \[\[Ravelry Operational Safety|Operational Safety]]
    - \[\[Ravelry Troubleshooting|Troubleshooting]]
