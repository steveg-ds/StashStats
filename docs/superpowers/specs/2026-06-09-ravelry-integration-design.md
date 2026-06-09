# Design Spec: Ravelry Web UI Expansion

## 1. Project Review & Bug Analysis

### Current Architecture
- **Tech Stack**: Python, Plotly Dash (Bootstrap themes), Redis (cache), SQLite (local db).
- **Current Scope**: Search yarns, add to stash, list/filter stash, log usage history, Plotly analytics.

### Critical Issues & Technical Debt
1. **Developer-only Auth (Basic Auth)**:
   - App uses basic auth with developer keys (`API_USERNAME`/`API_KEY`) and hardcoded/env `RAVELRY_USERNAME`.
   - Cannot support multiple users. Needs OAuth 2.0 flow.
2. **Synchronous API Bottlenecks**:
   - Heavy network calls during page loads (e.g., `get_stash_list` pagination).
   - App is slow if Ravelry is rate-limiting or down.
3. **Write-Through Deficiencies**:
   - Usage logging is written to local SQLite `stash_history` but not synced back to Ravelry (Ravelry has no native history endpoint; history events are local-only and can drift if Ravelry stash is modified externally).
4. **Rate Limit Handling**:
   - Ravelry API has strict rate limits. Concurrent API calls inside ThreadPoolExecutors risk 429 errors under load.

---

## 2. Ravelry API Feature Mapping

Based on `Ravelry API Documentation.html`, these premium capabilities can be integrated:

| Capability | Endpoints | UI Elements |
|---|---|---|
| **Unified Stash** | `GET /stash/unified/list.json`, `GET /fiber/{id}.json` | Combines yarn and fiber stashes into a single grid view. |
| **Project Tracker** | `GET/POST/PUT/DELETE /projects/{username}` | List projects, change status (active/finished), track needle sizes used, view photos. |
| **Needle Organizer** | `GET /needles/list.json`, `/needles/sizes.json` | Visual inventory of owned knitting needles and crochet hooks. |
| **Queue Manager** | `GET/POST/PUT/DELETE /queue/{username}` | Drag-and-drop or reorder cards for queued projects. |
| **Pattern Library** | `GET /library/search.json` | Search purchased/free PDFs saved in the user's Ravelry library. |

---

## 3. Proposed Approaches

### Approach A: Live API Wrap (with Redis caching)
- **Design**: All tabs request Ravelry API directly on load. Use Redis with short TTLs (5-10m) to reduce API hits.
- **Pros**: Easy to implement. No database schema drift.
- **Cons**: High latency. App breaks offline. API rate-limit risk.

### Approach B: SQLite Sync Engine (Recommended)
- **Design**: Sync Ravelry data into local SQLite database. All reads served from SQLite. Sync triggered in background (celery or cron) or manually via "Sync" button. Writes update both SQLite and Ravelry.
- **Pros**: Instant load times (under 50ms). Offline support. Safe from API rate limits.
- **Cons**: Requires complex sync/diff logic to handle external updates.

---

## 4. Sub-Project 1: Stash & Project Sync Engine
For the first iteration, we focus on:
1. **OAuth 2.0 Authorization flow**: Let users log in via Ravelry.
2. **Projects Tab**: View/edit project list synced to SQLite.
3. **Needles Viewer**: Simple read-only inventory list.
