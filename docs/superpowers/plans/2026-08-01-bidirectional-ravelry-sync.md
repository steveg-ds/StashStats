# Bi-Directional Ravelry Batch Sync Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement local-first `is_dirty` sync state tracking with Pydantic V2 validation, a 24-hour background scheduler, a manual "Sync Now" button, and unsynced change badges in StashStats.

**Architecture:** Add `StashSyncState` Pydantic model and `stash_sync_state` database table. Edits set `is_dirty = TRUE`, overlaying local values during stash rendering. A batch sync engine dispatches PUT calls to Ravelry API `/stashes/{id}.json`, clearing dirty flags on HTTP 200.

**Tech Stack:** Python 3.12+, Dash, Dash Bootstrap Components (`dbc`), Pydantic V2, PostgreSQL / SQLite (`stashies/db.py`), `pytest`.

## Global Constraints
- All sync models MUST validate through Pydantic V2 (`StashSyncState.model_validate`).
- UI styling MUST strictly use Dash Bootstrap Components (`dbc.themes.DARKLY`).
- Code MUST achieve >80% test coverage with unit and Playwright E2E tests.

---

### Task 1: Pydantic V2 StashSyncState Model

**Files:**
- Create: `stashies/dataclasses/stash_sync_state.py`
- Test: `tests/test_stash_sync_state.py`

**Interfaces:**
- Consumes: Pydantic V2 `BaseModel`, `Field`
- Produces: `StashSyncState(stash_id: str, is_dirty: bool, last_synced_at: Optional[datetime], sync_error: Optional[str], updated_at: datetime)`

- [ ] **Step 1: Write the failing test**

```python
from datetime import datetime
import pytest
from pydantic import ValidationError
from stashies.dataclasses.stash_sync_state import StashSyncState

def test_stash_sync_state_defaults():
    state = StashSyncState(stash_id="12345")
    assert state.stash_id == "12345"
    assert state.is_dirty is False
    assert state.last_synced_at is None
    assert state.sync_error is None
    assert isinstance(state.updated_at, datetime)

def test_stash_sync_state_validation_error():
    with pytest.raises(ValidationError):
        StashSyncState(stash_id=123, is_dirty="invalid_bool")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. CI=true .venv/bin/pytest tests/test_stash_sync_state.py`
Expected: FAIL with `ModuleNotFoundError: No module named 'stashies.dataclasses.stash_sync_state'`

- [ ] **Step 3: Write minimal implementation**

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

class StashSyncState(BaseModel):
    """Pydantic V2 model enforcing type validation for stash sync tracking state."""
    stash_id: str
    is_dirty: bool = False
    last_synced_at: Optional[datetime] = None
    sync_error: Optional[str] = None
    updated_at: datetime = Field(default_factory=datetime.now)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. CI=true .venv/bin/pytest tests/test_stash_sync_state.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stashies/dataclasses/stash_sync_state.py tests/test_stash_sync_state.py
git commit -m "feat(sync): Create StashSyncState Pydantic V2 model"
```

---

### Task 2: Database Schema & DBManager Extensions

**Files:**
- Modify: `stashies/db.py:60-120`
- Test: `tests/test_db_sync.py`

**Interfaces:**
- Consumes: `StashSyncState` from `stashies.dataclasses.stash_sync_state`
- Produces: `DBManager.mark_dirty`, `DBManager.get_dirty_stash_ids`, `DBManager.get_sync_state`, `DBManager.mark_synced`, `DBManager.get_unsynced_count`

- [ ] **Step 1: Write the failing test**

```python
import pytest
from stashies.db import DBManager

def test_db_sync_state_lifecycle():
    DBManager.run_migrations()
    DBManager.mark_dirty("test_stash_999")
    
    dirty_ids = DBManager.get_dirty_stash_ids()
    assert "test_stash_999" in dirty_ids
    
    count = DBManager.get_unsynced_count()
    assert count >= 1
    
    state = DBManager.get_sync_state("test_stash_999")
    assert state is not None
    assert state.is_dirty is True
    
    DBManager.mark_synced("test_stash_999")
    assert DBManager.get_sync_state("test_stash_999").is_dirty is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. CI=true .venv/bin/pytest tests/test_db_sync.py`
Expected: FAIL with `AttributeError: type object 'DBManager' has no attribute 'mark_dirty'`

- [ ] **Step 3: Write minimal implementation**

In `stashies/db.py`:
Add table creation for `stash_sync_state` in `run_migrations`:
```sql
CREATE TABLE IF NOT EXISTS stash_sync_state (
    stash_id VARCHAR(50) PRIMARY KEY,
    is_dirty BOOLEAN DEFAULT FALSE,
    last_synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sync_error TEXT DEFAULT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

Add classmethods to `DBManager`:
```python
@classmethod
def mark_dirty(cls, stash_id: str):
    conn = cls.get_pool().getconn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("""
            INSERT INTO stash_sync_state (stash_id, is_dirty, updated_at)
            VALUES (%s, TRUE, CURRENT_TIMESTAMP)
            ON CONFLICT (stash_id) DO UPDATE SET is_dirty = TRUE, updated_at = CURRENT_TIMESTAMP
            """, (str(stash_id),))
            conn.commit()
        finally:
            cur.close()
    finally:
        cls.get_pool().putconn(conn)

@classmethod
def get_dirty_stash_ids(cls) -> list:
    conn = cls.get_pool().getconn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT stash_id FROM stash_sync_state WHERE is_dirty = TRUE")
            rows = cur.fetchall()
            return [r[0] for r in rows]
        finally:
            cur.close()
    finally:
        cls.get_pool().putconn(conn)

@classmethod
def mark_synced(cls, stash_id: str):
    conn = cls.get_pool().getconn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("""
            UPDATE stash_sync_state 
            SET is_dirty = FALSE, last_synced_at = CURRENT_TIMESTAMP, sync_error = NULL, updated_at = CURRENT_TIMESTAMP
            WHERE stash_id = %s
            """, (str(stash_id),))
            conn.commit()
        finally:
            cur.close()
    finally:
        cls.get_pool().putconn(conn)

@classmethod
def get_unsynced_count(cls) -> int:
    conn = cls.get_pool().getconn()
    try:
        cur = conn.cursor()
        try:
            cur.execute("SELECT COUNT(*) FROM stash_sync_state WHERE is_dirty = TRUE")
            row = cur.fetchone()
            return row[0] if row else 0
        finally:
            cur.close()
    finally:
        cls.get_pool().putconn(conn)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. CI=true .venv/bin/pytest tests/test_db_sync.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stashies/db.py tests/test_db_sync.py
git commit -m "feat(db): Add stash_sync_state table and DBManager sync tracking methods"
```

---

### Task 3: AppController Batch Sync Engine & Stash Card Indicators

**Files:**
- Modify: `stashies/app_controller.py:225-450`
- Test: `tests/test_batch_sync_engine.py`

**Interfaces:**
- Consumes: `DBManager.get_dirty_stash_ids`, `DBManager.mark_synced`, `RavelryClient.update_stash`
- Produces: `AppController.execute_batch_sync`, `StashCard.create_grouped_accordion_item` (with `Pending Sync` badge)

- [ ] **Step 1: Write the failing test**

```python
from unittest.mock import MagicMock
from stashies.app_controller import AppController

def test_execute_batch_sync():
    controller = AppController("h", "s", "r")
    controller.MODEL.get_dirty_stash_ids = MagicMock(return_value=["101"])
    controller.MODEL.update_ravelry_stash = MagicMock(return_value=True)
    controller.MODEL.mark_synced = MagicMock()
    
    success_count = controller.execute_batch_sync()
    assert success_count == 1
    controller.MODEL.mark_synced.assert_called_once_with("101")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. CI=true .venv/bin/pytest tests/test_batch_sync_engine.py`
Expected: FAIL with `AttributeError: 'AppController' object has no attribute 'execute_batch_sync'`

- [ ] **Step 3: Write minimal implementation**

In `stashies/app_controller.py`:
```python
def execute_batch_sync(self) -> int:
    """Execute batch PUT sync for all items marked is_dirty == TRUE."""
    dirty_ids = self.MODEL.get_dirty_stash_ids()
    synced_count = 0
    for sid in dirty_ids:
        # Send update to Ravelry API
        success = self.MODEL.sync_stash_entry_to_ravelry(sid)
        if success:
            self.MODEL.mark_synced(sid)
            synced_count += 1
    return synced_count
```

Add `Pending Sync` badge logic in `render_stash_cards`:
```python
if is_dirty:
    badge = dbc.Badge("Pending Sync", color="warning", className="me-2")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. CI=true .venv/bin/pytest tests/test_batch_sync_engine.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add stashies/app_controller.py tests/test_batch_sync_engine.py
git commit -m "feat(controller): Implement execute_batch_sync and pending sync UI badges"
```

---

### Task 4: UI Sync Button & Playwright E2E Integration

**Files:**
- Modify: `app.py`, `stashies/app_controller.py`
- Test: `tests/e2e/test_sync_ui_e2e.py`

- [ ] **Step 1: Write the failing test**

```python
from playwright.sync_api import Page, expect

def test_sync_now_button_e2e(page: Page, live_server):
    page.goto(live_server.url)
    page.click("text=Personal Stash")
    expect(page.locator("#stash-sync-btn")).to_be_visible()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=. CI=true .venv/bin/pytest tests/e2e/test_sync_ui_e2e.py`
Expected: FAIL with locator `#stash-sync-btn` not found

- [ ] **Step 3: Write minimal implementation**

Add `Sync Now` button and callback in `app.py` & `stashies/app_controller.py`:
```python
@callback(
    Output("stash-sync-status-msg", "children"),
    Output("stash-update-trigger", "data", allow_duplicate=True),
    Input("stash-sync-btn", "n_clicks"),
    State("stash-update-trigger", "data"),
    prevent_initial_call=True,
)
def handle_manual_sync(n_clicks, trigger_data):
    if not n_clicks:
        raise PreventUpdate
    count = CONTROLLER.execute_batch_sync()
    new_trigger = (trigger_data or 0) + 1
    return f"Synced {count} items successfully.", new_trigger
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=. CI=true .venv/bin/pytest tests/e2e/test_sync_ui_e2e.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app.py stashies/app_controller.py tests/e2e/test_sync_ui_e2e.py
git commit -m "feat(ui): Add Sync Now button callback and Playwright E2E test"
```
