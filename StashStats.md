# StashStats

StashStats is a Dash-based web application for searching, tracking, and managing personal yarn stash data via the Ravelry API.

---
## TODOs

- [ ] How well is the system of using Ravelry's stash item update times for the plots in the other tab? 
## Current Features

### Yarn Search Tab
- Full-text yarn search against Ravelry's database
- Results show: name, company, weight (g), yardage, discontinued status, machine washability, colorway badges, yarn photo
- Each result has an inline **Add to Stash** form: skeins, colorway (dropdown if known, text if not), dye lot, location, notes
- Colorway selector populated from live Ravelry API colorway data
	- 

### Personal Stash Tab
- Full stash list for the configured Ravelry user (paginated, fetches all pages)
- Search/filter bar (fuzzy match on yarn name, brand, colorway)
- Each card shows: yarn photo, name, brand, colorway, dye lot, location, quantity (skeins / yards / meters / grams), status badge
- **Edit modal** (two tabs):
  - *Edit Details*: update colorway, dye lot, location, skeins (exact), status, notes
  - *Log Usage*: enter skeins consumed — live preview of remaining — saves new total to Ravelry
- All writes go via Ravelry PUT API; local cache invalidated on success

### Stash Analytics Tab
- Cumulative stash metrics over time: Yards, Meters, Skeins, Weight (grams)
- Metric selector dropdown (individual or 2×2 All Metrics grid view)
- Summary stat cards at top (current totals, highlighted by selected metric)
- Consumption tracking:
  - Yarn linked to completed projects → subtracted at project completion date
  - Yarn with status "Used up" (2) or "Gone/Sold" (4) → subtracted at `updated_at` date
  - Partial usage tracked via delta history (cache compares old vs new pack values on each refresh)
- History events stored in `stash_cache.json` (never lost across refreshes)

### Dev / Ops
- File-based write logging to `dev_changes.log` (rotating, 1 MB max)
- Stash detail cache (`stash_cache.json`) with `updated_at` sentinel to avoid redundant API calls
- Concurrent detail fetching (ThreadPoolExecutor, 3 workers, 0.2s rate-limit delay)

---

## Architecture

```
app.py                          ← Dash app, all callbacks, modal definitions
stashies/
  app_controller.py             ← Layout builder + search orchestration
  model.py                      ← Data layer: search_yarn, get_stash_list,
                                   create_stash, update_stash, get_full_yarn
  base_req.py                   ← HTTP client (GET/POST/PUT) with Basic Auth
  base.py                       ← Base class; injects LOGGER into subclasses
  components/
    base_component.py           ← Pydantic dataclass base for layout components
    header.py                   ← Logo + HR header
    search.py                   ← Search bar, category/sort dropdowns
    search_results.py           ← AccordionItem builder + stash form per result
  dataclasses/
    yarn.py                     ← Pydantic Yarn schema (validates API response)
    yarn_photos.py              ← YarnPhotos with placeholder fallback URLs
    colorway.py                 ← Colorway schema
    stash_post.py               ← StashPost / PackPost schema for create payload
    yarn_company.py             ← YarnCompany schema
  utils/
    logger_func.py              ← create_logger() with optional RotatingFileHandler
    model_config.py             ← Shared Pydantic model config

stash_cache.json                ← Local pack/history/original_values cache
dev_changes.log                 ← Dev write audit log (remove for prod)
tests/
  test_e2e.py                   ← Playwright E2E + unit tests (thread-based server)
```

### App.py

- Sets up initial app layout → CONTROLLER.create_initial_layout()

### AppController.py




---

## Known Bugs / Active TODOs

### 🔴 Critical

- [ ] **`Optional`/`List` not imported in `search_results.py:21`** — used in function signature but never imported. `NameError` at runtime on every search result render. Fix: `from typing import Optional, List`.
- [ ] **`data['yarns']` no key guard in `model.py:75`** — if API returns `{}` or omits `yarns` key, raises `KeyError` before function can return `None`. Fix: use `data.get('yarns')` with guard.
- [ ] **`os.getenv("USERNAME")` collides with Linux shell variable** — on Linux, `USERNAME` is set by the shell to the OS user (e.g. `thotsky`). If `.env` doesn't explicitly override it, Ravelry API calls silently hit wrong user's stash. Same issue in `app.py:341`, `model.py:84`, `model.py:210`. Fix: rename env var to `RAVELRY_USERNAME`.
- [ ] **`MagicMock` imported after use in `tests/test_e2e.py:57`** — `MagicMock` used inside `mock_get` defined at line 57 but not imported until line 99 → `NameError` when mock is called. Fix: move import to top of test function.

### 🟡 Warnings

- [ ] **Edit modal doesn't show yarn name** — modal title says "Edit Stash Entry" with no yarn identification. Fix: pass yarn name into `dcc.Store` data; display in modal header.
- [ ] **First stash card may auto-open edit modal on tab load** — pattern-matched `n_clicks=None` check may fire on initial layout render. Fix: add `if not any(c for c in edit_clicks if c): raise PreventUpdate`.
- [ ] **Stash list doesn't auto-refresh after edit** — must manually switch tabs and return. Fix: output to `stash-list-container` from save callback, or add `dcc.Interval`.
- [ ] **Subtraction loop doesn't skip child packs** (`app.py:433-462`) — positive acquisition loop correctly skips `primary_pack_id is not None` packs, but the subtraction loop does not, double-counting yardage removed for multi-pack entries.
- [ ] **`search-category` State wired but ignored** (`app.py:239`) — category filter silently dropped in `handle_search`. Fix: pass to `CONTROLLER.search_yarn` or remove from callback inputs.
- [ ] **`search-sort` value mismatch** — UI sends `"best_match"` but Ravelry API expects `"best"`. Fix: map UI value to API value before calling search.
- [ ] **Project fetch not paginated** (`app.py:344`) — `projects/list.json` fetched with `page_size=100` only. Users with >100 projects miss older project dates. Fix: paginate like stash list.
- [ ] **Cache `updated_at` removed but `original_values`/`history` kept on invalidation** (`model.py:update_stash`) — after a write, `updated_at` sentinel removed so next fetch re-fetches details, but the *new* pack totals are then compared against the existing cached packs (stale), generating a spurious zero-or-wrong delta. Fix: also zero out `packs` in cache on invalidation.
- [ ] **`time.sleep(0.2)` in ThreadPoolExecutor doesn't serialize requests** (`model.py:129`) — 3 workers all sleep then burst simultaneously. Fix: use a threading `Semaphore` + sleep, or reduce `max_workers=1`.
- [ ] **`stash_cache.json` not atomic write** (`model.py:200`) — concurrent requests or crash mid-write corrupts cache. Fix: write to temp file → `os.replace()`.
- [ ] **`stash_cache.json` relative path** (`model.py:105`) — resolves to CWD, not guaranteed to be project root. Fix: use `Path(__file__).parent.parent / "stash_cache.json"`.
- [ ] **`stash_cache.json` grows unboundedly** — deleted stash entries never removed. Fix: after fetching live stash, remove cache keys not in current ID set.
- [ ] **`stash_post.py` schema unused** — `StashPost`/`PackPost` defined but `create_stash` builds raw dicts. Fix: validate payload against schema before POST.
- [ ] **`memory-output` Store dead code** — `dcc.Store(id='memory-output')` in layout, no callbacks use it. Remove.
- [ ] **`btn_ids` / `store_data_list` ordering assumption** (`app.py:943`) — assumes 1:1 DOM order between `ALL` pattern outputs. Not guaranteed on dynamic add/remove. Low risk currently but could silently populate wrong entry's modal data.
- [ ] **`payload = {"pack": {"skeins": remaining}}` partial pack update** (`app.py:1051`) — sends only skeins; verify Ravelry API contract for partial pack PUT (may need pack `id` to update correct pack vs creating new one).
- [ ] **History event bare key access** (`app.py:474`) — `event["date"]`, `event["yards"]` etc. crash on malformed history entries. `except Exception: pass` silently swallows — data lost without trace. Fix: use `.get()` with explicit skip + log.
- [ ] **`yarn.py:71` `v['name']` no guard** — `KeyError` if API returns company dict without `name` key. Fix: `v.get('name', '')`.
- [ ] **`dash_server` test fixture strips environment** (`tests/test_e2e.py:12`) — `env` dict fully replaces env; PATH missing; subprocess may fail to find shared libs. Fix: `{**os.environ, "API_USERNAME": ..., ...}`.
- [ ] **`test_stash_yarn_flow` is a no-op** (`tests/test_e2e.py:29`) — body is `pass`, silently passes with no assertions. Fix: implement or `pytest.mark.skip`.

### 🔵 Minor

- [ ] **`sorted(set(...))` order in `yarn.py:53`** — `list(set(sorted(...)))` destroys sort order (`set` is unordered). Fix: `sorted(set([c['name'] for c in v]))`.
- [ ] **`random.choice(v)` for photo selection** (`yarn.py:65`) — non-deterministic; different photo shown each render. Fix: `v[0]` for consistency.
- [ ] **`dev_changes.log` always-on** — should be gated by `DEV_LOGGING=1` env var for production.
- [ ] **`0.9144` yards-to-meters constant duplicated** — appears in 5+ places across `app.py` and `model.py`. Extract to module-level constant.
- [ ] **`if photos and len(photos) > 0`** (`app.py:792`) — `len > 0` redundant. Use `if photos`.
- [ ] **Test `time.sleep(3)` flaky on slow CI** — use retry poll loop instead.
- [ ] **E2E tests lack cache cleanup between runs** — analytics test makes cache non-deterministic across re-runs. Fix: delete/mock `stash_cache.json` in test fixture teardown.
- [ ] **No tests for edit modal, Log Usage, or `update_stash`** — entire write path untested.

---

## Potential Improvements / Feature Ideas

### UX / UI
- **Stash list sorting** — currently unsorted (API order). Add sort-by: quantity, date added, yarn weight, brand name.
- [ ] **Stash list pagination / virtual scroll** — 164 items renders all at once; slow on large stashes. Add `page_size` + pagination controls or `dash-ag-grid` virtual list. 
	- sort by most recently added or edited
- **Stash list grouping** — group by fiber type, yarn weight, brand, or status.
- **Stash entry detail view** — click a card to see full detail (fiber breakdown, yarn attributes, all photos, linked projects).
- **Bulk status update** — select multiple entries → mark all as "Used up" or change location.
- **Yarn weight / fiber filter** — filter stash by weight category (DK, Worsted, etc.) or fiber type (wool, cotton, acrylic).
- **Search by colorway within stash** — currently only name/brand/colorway text search; add color family filter.
- **Photo carousel** — yarn entries with multiple photos only show one. Carousel or thumbnail strip.

### Analytics
- **Acquisition rate chart** — yards/skeins acquired per month bar chart alongside cumulative line.
- [ ] **Consumption vs acquisition** — side-by-side to show net stash growth/shrinkage over time.
- **Project usage timeline** — overlay project completion dates on the cumulative plot.
- [ ] **Stash age heatmap** — calendar heatmap of acquisition dates.

### Data / Backend
- [ ] **In-memory caching (Redis or functools.lru_cache)** — current file cache avoids API hits but has race condition risk; proper cache layer would handle TTL and concurrent access safely.
	- eventually will run app in docker compose stack, can use redis there
- **Cache warm-up on startup** — pre-fetch stash in background thread at app start so first tab visit is fast.
- [ ] **Ravelry OAuth flow** — current personal Basic Auth token works for singl e-user; multi-user deployment needs OAuth. Client ID/secret already in `.env`.
	- very long term worry, not now
- **`update_stash` validation** — validate payload against a `StashPut` Pydantic schema before sending to API (catches bad types early).
- [ ] **DELETE stash entry** — not yet exposed in UI. Ravelry API supports `DELETE /people/{user}/stash/{id}.json`.
	- good idea but needs browser confirmation since can't be undone
- **PATCH yards_per_skein** — allow overriding per-skein yardage when Ravelry's default is wrong (common for indie dyers).
- **Export stash to CSV/JSON** — download button on Personal Stash tab.
- **Import from CSV** — bulk-add stash entries from spreadsheet.

### Testing
- **Unit tests for analytics data-building logic** — the `update_analytics_content` callback is complex and untested at unit level.
- **Test for edit modal population** — verify `toggle_edit_modal` populates fields correctly from store data.
- **Test for `update_stash` write path** — mock PUT, verify payload structure and cache invalidation.
- **Test for `Log Usage` math** — verify `remaining = max(0, current - used)` edge cases (used > current, used = 0, fractional).
- **Playwright tests for stash tab** — no E2E test covers Personal Stash tab load, filtering, or edit modal.
- **Test concurrent cache writes** — verify no data corruption under parallel requests.

### Ops / Dev
- **Gate `dev_changes.log` behind env var** — `DEV_LOGGING=1` enables file logging; off by default.
- **`.gitignore` `stash_cache.json` and `dev_changes.log`** — both contain user data / ephemeral logs; shouldn't be committed.
- **`PYTHONPATH=.` requirement** — running `app.py` requires manual env var; fix with proper package install or `pyproject.toml` entry point.
- **Pin dependency versions** — `requirements.txt` or `pyproject.toml` with pinned versions for reproducible installs.
- **Health check endpoint** — `/health` Flask route returning 200 for load balancer / uptime monitoring.

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

> **Note:** The read-only Basic Auth credentials (`read-...`) will cause 403 on all write operations (edit, log usage, add to stash). Use the **personal** credentials.

### 3. Start Application

```bash
PYTHONPATH=. .venv/bin/python app.py
```

App runs at http://127.0.0.1:8050

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

| File | Purpose |
|---|---|
| `app.py` | Dash app + all callbacks (search, stash list, analytics, edit modal) |
| `stashies/app_controller.py` | Tab layout + search result rendering |
| `stashies/model.py` | All Ravelry API calls + cache logic |
| `stashies/base_req.py` | Raw HTTP GET/POST/PUT with Basic Auth |
| `stashies/base.py` | Logger injection base class |
| `stashies/components/search.py` | Search bar UI component |
| `stashies/components/search_results.py` | Search result card + add-to-stash form |
| `stashies/components/header.py` | Logo header |
| `stashies/dataclasses/yarn.py` | Pydantic Yarn validation schema |
| `stashies/dataclasses/yarn_photos.py` | Photo URL container with fallback |
| `stashies/dataclasses/stash_post.py` | StashPost/PackPost schema (unused in create path) |
| `stashies/utils/logger_func.py` | Logger factory with optional file handler |
| `stashies/utils/model_config.py` | Shared Pydantic config |
| `stash_cache.json` | Local stash detail cache (do not commit) |
| `dev_changes.log` | Write audit log for dev (do not commit) |
| `tests/test_e2e.py` | Playwright E2E + unit tests |
| `Stash Object Analysis.md` | Ravelry stash API response field reference |
| `stash_stats_code_review.md` | Previous OAuth implementation code review |
