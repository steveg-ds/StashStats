# Implementation Plan: Fix Personal Stash and Stash Analytics Loading Failure

## Phase 1: Diagnostic & Regression Test Creation
- [ ] Task: Reproduce issue and write regression unit tests
    - [ ] Inspect server logs and test `DBManager` connection pooling under Dash callback conditions
    - [ ] Write failing regression test reproducing the tab loading failure (TDD Red phase)
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Diagnostic & Regression Test Creation' (Protocol in workflow.md)
    - [ ] Agent verification: Automatically execute regression test `PYTHONPATH=. CI=true .venv/bin/pytest tests/` and inspect stack traces

## Phase 2: Code Fix & Verification
- [ ] Task: Resolve database connection / query issues in DBManager and callbacks
    - [ ] Fix connection pool release, lock, or query execution bug in `stashies/db.py` / `stashies/app_controller.py`
    - [ ] Verify regression tests and full test suite pass cleanly (TDD Green phase)
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Code Fix & Verification' (Protocol in workflow.md)
    - [ ] Agent verification: Automatically run `PYTHONPATH=. CI=true .venv/bin/pytest tests/` and verify server startup logs
