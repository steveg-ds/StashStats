# Track: codebase_hardening_20260801 — Implementation Plan

## Phase 1: Database Safety (conn.rollback + datetime fix)

- [ ] Task: Write failing tests for rollback behavior
    - [ ] Add test asserting pool connection is returned clean when commit fails
    - [ ] Add test for StashSyncState with timezone-aware datetime
- [ ] Task: Add `conn.rollback()` to all DB write methods
    - [ ] `stashies/db.py` line 131 (save_stash_data or equivalent)
    - [ ] `stashies/db.py` line 216
    - [ ] `stashies/db.py` line 237
    - [ ] `stashies/db.py` line 291
    - [ ] `stashies/db.py` line 390
    - [ ] `stashies/db.py` line 429
    - [ ] `stashies/db.py` line 497
    - [ ] `stashies/db.py` line 549
- [ ] Task: Fix naive datetime in StashSyncState
    - [ ] Change `datetime.now` to `datetime.now(timezone.utc)` in `stashies/dataclasses/stash_sync_state.py`
    - [ ] Import `timezone` from `datetime`
- [ ] Task: Commit Phase 1 code
- [ ] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)

## Phase 2: Network Layer & App Safety

- [ ] Task: Write failing tests for WeatherClient retry
    - [ ] Test that transient network error triggers retry
    - [ ] Test that malformed JSON raises/returns typed error
- [ ] Task: Add retry logic to WeatherClient
    - [ ] Use `requests.adapters.HTTPAdapter` with `urllib3.util.retry.Retry`
    - [ ] Validate API response shape before access (check `daily` key exists)
    - [ ] Return typed result or raise instead of silent empty list
- [ ] Task: Fix `debug=True` hardcode in app.py
    - [ ] Read `APP_DEBUG` env var with `os.getenv('APP_DEBUG', 'false').lower() == 'true'`
- [ ] Task: Replace bare excepts in AppController
    - [ ] `app_controller.py` line 405: catch `ValueError`
    - [ ] `app_controller.py` line 913: catch `json.JSONDecodeError`
    - [ ] `app_controller.py` line 945: catch specific string/parse exception
- [ ] Task: Commit Phase 2 code
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: Test Suite Hardening

- [ ] Task: Fix E2E test assertions in test_inventory_edit_e2e.py
    - [ ] `test_stash_edit_modal`: add `expect(page.locator(...)).to_be_visible()`
    - [ ] `test_stash_quantity_update`: assert updated quantity value in DOM
    - [ ] `test_usage_history_entries`: assert entry count > 0 or specific content
- [ ] Task: Fix E2E test assertions in test_search_filter_e2e.py
    - [ ] Replace `assert count >= 0` with `assert count > 0`
    - [ ] `test_search_debounce`: add debounce result assertion
    - [ ] `test_filter_schedule_changes`: add filter result assertion
- [ ] Task: Fix unit test assertions
    - [ ] `test_temperature_modal.py`: assert specific child components exist, not just `is not None`
    - [ ] `test_temperature_ravelry_link.py`: add `mock_create.assert_called_once_with(...)`
- [ ] Task: Fix MockDBManager state leakage in test_e2e.py
    - [ ] Clear class-level mutable dicts in fixture teardown or use instance dicts
    - [ ] Remove dead code after `return 0` (line 121)
    - [ ] Scope `sys.modules['redis']` patch within fixture using `mock.patch.dict`
- [ ] Task: Run full test suite and verify no regressions
    - [ ] `PYTHONPATH=. CI=true .venv/bin/pytest tests/ -v`
- [ ] Task: Commit Phase 3 code
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)
