# Track: Codebase Hardening

## Overview
A systematic hardening pass fixing critical reliability, correctness, and test quality issues identified in a deep audit of the StashStats codebase.

## Problems Being Fixed

### P1 — Missing `conn.rollback()` in DB methods (CRITICAL)
- All write methods in `stashies/db.py` call `conn.commit()` inside try blocks but do NOT call `conn.rollback()` in the except block
- Failed commits return poisoned connections to the pool → cascading failures
- Affected lines: 131, 216, 237, 291, 390, 429, 497, 549

### P2 — Naive datetime in StashSyncState (CRITICAL)
- `StashSyncState.updated_at` uses `datetime.now` (timezone-naive)
- Postgres TIMESTAMP columns with timezone require aware datetimes
- Causes comparison bugs and potential insertion errors

### P3 — Exception swallowing in client/base.py (HIGH)
- All 4 HTTP methods (get/post/put/delete) catch bare `Exception` and swallow silently
- Callers have no way to detect network failures

### P4 — `debug=True` hardcoded in app.run() (MEDIUM)
- RCE risk if deployed directly via `python app.py`
- Must be controlled via environment variable

### P5 — WeatherClient lacks retry and response validation (MEDIUM)
- No retry logic on transient network errors
- API JSON response shape not validated before access
- Error returns empty list silently (caller cannot distinguish "no data" from "API down")

### P6 — Test suite false confidence (HIGH)
- Multiple E2E and unit tests pass by not crashing rather than asserting behavior
- `assert count >= 0` always passes
- `assert layout is not None` does not verify content
- MockDBManager leaks class-level state between tests
- `sys.modules['redis']` patch leaks globally

### P7 — AppController bare excepts (MEDIUM)
- Lines 405, 913, 945 use bare `except` with `pass` or silent swallow

## Acceptance Criteria
- All DB write methods have `conn.rollback()` in except blocks
- `StashSyncState.updated_at` uses `datetime.now(timezone.utc)`
- `app.run()` reads debug flag from `APP_DEBUG` env var
- WeatherClient has retry with `requests.adapters.HTTPAdapter` + `Retry`
- WeatherClient validates API response shape before access
- All E2E tests have meaningful `expect()` or `assert` statements verifying actual behavior
- MockDBManager state cleared between tests
- AppController bare excepts replaced with specific exception types
- All existing tests continue to pass (no regressions)

## Out of Scope
- Implementing `sync_stash_entry_to_ravelry` real API calls (separate track)
- Implementing `create_ravelry_project` real API calls (separate track)
- Filling `create_temperature_project` DB method usage (separate track)
- Exception re-raising (logged-and-swallowed pattern stays for now — just make it intentional)
