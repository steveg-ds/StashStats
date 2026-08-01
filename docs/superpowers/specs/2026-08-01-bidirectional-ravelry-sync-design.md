# Design Spec: Bi-Directional Ravelry Batch Sync & Unsynced Change Tracking

## Overview
This specification details the design for bi-directional synchronization between local StashStats storage and Ravelry's stash API. It introduces local dirty-state tracking, a 24-hour background sync timer, a manual "Sync Now" trigger on the Personal Stash page, and visual indicators for non-synced changes.

---

## 1. Objectives & Requirements
- **Local-First Reliability:** Allow instant editing of yarn stash quantities, location, notes, and usage history without waiting for Ravelry API network calls.
- **Unsynced Change Tracking:** Visually notify users of pending local edits both globally (header badge) and per item (stash card badge).
- **Background & Manual Sync:** Automatically sync pending changes to Ravelry every 24 hours, while allowing manual "Sync Now" execution.
- **Resilience Against API Timestamps:** Use a local `is_dirty` boolean flag and local state locking instead of unreliable Ravelry API modification timestamps.

---

## 2. Architecture & Data Flow

```
[Dash UI (Personal Stash)] ──(Local Edit)──> [DBManager / PostgreSQL]
                                                      │
                                                      │ (is_dirty = TRUE)
                                                      ▼
[Stash List Render] <──(Overlay Local Edits)── [Local DB Cache]
                                                      │
                                                      │ (Sync Now / 24h Cron)
                                                      ▼
                                           [Batch Sync Engine]
                                                      │
                                                      │ (PUT /stashes/{id}.json)
                                                      ▼
                                            [Ravelry API Endpoint]
                                                      │
                                                      │ (200 OK Response)
                                                      ▼
                                           [is_dirty = FALSE, NOW()]
```

---

## 3. Database Schema Changes (`stashies/db.py`)

Create table `stash_sync_state`:

```sql
CREATE TABLE IF NOT EXISTS stash_sync_state (
    stash_id VARCHAR(50) PRIMARY KEY,
    is_dirty BOOLEAN DEFAULT FALSE,
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_error TEXT DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Operations
- `DBManager.mark_dirty(stash_id: str)`: Sets `is_dirty = TRUE` for target `stash_id`.
- `DBManager.get_dirty_stash_ids() -> List[str]`: Retrieves all stash IDs with pending changes.
- `DBManager.mark_synced(stash_id: str)`: Sets `is_dirty = FALSE`, updates `last_synced_at = NOW()`, and clears `sync_error`.
- `DBManager.get_unsynced_count() -> int`: Returns total number of pending items.

---

## 4. UI/UX Component Specifications

### 4.1 Personal Stash Page Header (`tab-stash`)
- **"Sync Now" Button:** `dbc.Button` containing an active badge displaying pending count (`dbc.Badge(f"{count} pending", color="warning")`).
- **Last Synced Timestamp Label:** `html.Span("Last synced: Today at 10:15 AM", className="text-muted ms-2")`.
- **Loading Spinner:** Wrapped in `wrap_with_loading` / `dcc.Loading` to show active network request status.

### 4.2 Stash Card Component (`StashCard`)
- For items where `is_dirty == TRUE`:
  - Display warning badge in card header: `dbc.Badge("Pending Sync", color="warning", className="me-2")`.
  - Stash card display values prioritize local database state over remote API responses.

---

## 5. Sync Engine Logic (`AppController.execute_batch_sync`)

1. Query all `stash_id`s from `stash_sync_state` where `is_dirty == TRUE`.
2. For each pending item, construct `StashPost` payload from local `original_values` and `stash_history` totals.
3. Call `RavelryClient.update_stash(stash_id, payload)`.
4. On Success (HTTP 200):
   - Call `DBManager.mark_synced(stash_id)`.
5. On Failure (Network error, HTTP 4xx/5xx):
   - Record error details in `sync_error`.
   - Keep `is_dirty = TRUE` for retry on next sync interval.
6. Refresh UI components and update last synced timestamp.

---

## 6. Error Handling & Edge Cases
- **Offline / Rate Limited:** Local edits persist safely in PostgreSQL/SQLite. Batch sync retries on next background interval or manual click.
- **Ravelry API Failure:** Display error alert toast in Dash UI detailing failed items while preserving local data integrity.
- **Deletion Sync:** Deleting a stash item marks deletion in local sync queue before dispatching DELETE call to Ravelry.

---

## 7. Testing Strategy
- **Unit Tests (`tests/test_sync_engine.py`):**
  - Verify `mark_dirty` and `mark_synced` database state transitions.
  - Mock Ravelry API endpoints to test 200 OK and failure retry behavior.
- **Playwright E2E Tests (`tests/e2e/test_sync_ui_e2e.py`):**
  - Edit stash entry -> verify "Pending Sync" badge appears.
  - Trigger "Sync Now" -> verify badge clears and timestamp updates.
