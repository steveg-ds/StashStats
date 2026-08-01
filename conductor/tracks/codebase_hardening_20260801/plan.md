# Track: codebase_hardening_20260801 — Implementation Plan

## Phase 1: Database Safety (conn.rollback + datetime fix)

- [x] Task: Write failing tests for rollback behavior [ebea526ee2adc3297f44f74925724963e375e4f6]
    - [x] Add test asserting pool connection is returned clean when commit fails
    - [x] Add test for StashSyncState with timezone-aware datetime
- [x] Task: Add `conn.rollback()` to all DB write methods [ebea526ee2adc3297f44f74925724963e375e4f6]
    - [x] `stashies/db.py` line 131 (save_stash_data or equivalent)
    - [x] `stashies/db.py` line 216
    - [x] `stashies/db.py` line 237
    - [x] `stashies/db.py` line 291
    - [x] `stashies/db.py` line 390
    - [x] `stashies/db.py` line 429
    - [x] `stashies/db.py` line 497
    - [x] `stashies/db.py` line 549
- [x] Task: Fix naive datetime in StashSyncState [ebea526ee2adc3297f44f74925724963e375e4f6]
    - [x] Change `datetime.now` to `datetime.now(timezone.utc)` in `stashies/dataclasses/stash_sync_state.py`
    - [x] Import `timezone` from `datetime`
- [x] Task: Commit Phase 1 code [ebea526ee2adc3297f44f74925724963e375e4f6]
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) [ebea526ee2adc3297f44f74925724963e375e4f6]

## Phase 2: Network Layer & App Safety

- [x] Task: Write failing tests for WeatherClient retry [095daae0d806e75454006981b8e8eb86fe103640]
    - [x] Test that transient network error triggers retry
    - [x] Test that malformed JSON raises/returns typed error
- [x] Task: Add retry logic to WeatherClient [095daae0d806e75454006981b8e8eb86fe103640]
    - [x] Use `requests.adapters.HTTPAdapter` with `urllib3.util.retry.Retry`
    - [x] Validate API response shape before access (check `daily` key exists)
    - [x] Return typed result or raise instead of silent empty list
- [x] Task: Fix `debug=True` hardcode in app.py [095daae0d806e75454006981b8e8eb86fe103640]
    - [x] Read `APP_DEBUG` env var with `os.getenv('APP_DEBUG', 'false').lower() == 'true'`
- [x] Task: Replace bare excepts in AppController [095daae0d806e75454006981b8e8eb86fe103640]
    - [x] `app_controller.py` line 405: catch `ValueError`
    - [x] `app_controller.py` line 913: catch `json.JSONDecodeError`
    - [x] `app_controller.py` line 945: catch specific string/parse exception
- [x] Task: Commit Phase 2 code [095daae0d806e75454006981b8e8eb86fe103640]
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) [095daae0d806e75454006981b8e8eb86fe103640]

## Phase 3: Test Suite Hardening

- [x] Task: Fix E2E test assertions in test_inventory_edit_e2e.py [be118aa6155bc525aa0128f957264b54f1d527d4]
    - [x] `test_stash_edit_modal`: add `expect(page.locator(...)).to_be_visible()`
    - [x] `test_stash_quantity_update`: assert updated quantity value in DOM
    - [x] `test_usage_history_entries`: assert entry count > 0 or specific content
- [x] Task: Fix E2E test assertions in test_search_filter_e2e.py [be118aa6155bc525aa0128f957264b54f1d527d4]
    - [x] Replace `assert count >= 0` with `assert count > 0`
    - [x] `test_search_debounce`: add debounce result assertion
    - [x] `test_filter_schedule_changes`: add filter result assertion
- [x] Task: Fix unit test assertions [be118aa6155bc525aa0128f957264b54f1d527d4]
    - [x] `test_temperature_modal.py`: assert specific child components exist, not just `is not None`
    - [x] `test_temperature_ravelry_link.py`: add `mock_create.assert_called_once_with(...)`
- [x] Task: Fix MockDBManager state leakage in test_e2e.py [be118aa6155bc525aa0128f957264b54f1d527d4]
    - [x] Clear class-level mutable dicts in fixture teardown or use instance dicts
    - [x] Remove dead code after `return 0` (line 121)
    - [x] Scope `sys.modules['redis']` patch within fixture using `mock.patch.dict`
- [x] Task: Run full test suite and verify no regressions [be118aa6155bc525aa0128f957264b54f1d527d4]
    - [x] `PYTHONPATH=. CI=true .venv/bin/pytest tests/ -v`
- [x] Task: Commit Phase 3 code [be118aa6155bc525aa0128f957264b54f1d527d4]
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md) [be118aa6155bc525aa0128f957264b54f1d527d4]

