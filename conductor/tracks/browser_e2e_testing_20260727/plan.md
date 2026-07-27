# Implementation Plan: Comprehensive Playwright E2E Browser Testing Suite

## Phase 1: Test Environment & Fixture Setup
- [ ] Task: Set up Chromium Playwright dependencies and server fixtures
    - [ ] Install `pytest-playwright` and Chromium browser binaries with Fedora Linux system dependencies (`playwright install chromium` / `playwright install-deps chromium`)
    - [ ] Create `tests/e2e/conftest.py` configured for Chromium browser instances, app server lifecycle, and database isolation fixtures
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Test Environment & Fixture Setup' (Protocol in workflow.md)
    - [ ] Agent verification: Automatically execute `pytest tests/e2e/conftest.py` fixture checks

## Phase 2: Core E2E Test Suite Implementation
- [ ] Task: Implement Dashboard & Navigation E2E Tests
    - [ ] Write `tests/e2e/test_dashboard_e2e.py` testing dashboard layout and chart renders in Chromium
- [ ] Task: Implement Search & Filter E2E Tests
    - [ ] Write `tests/e2e/test_search_filter_e2e.py` testing pattern/yarn search inputs and debounced filtering
- [ ] Task: Implement Stash Edit & Usage History E2E Tests
    - [ ] Write `tests/e2e/test_inventory_edit_e2e.py` testing modal popups, stash quantity updates, and usage history entries
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core E2E Test Suite Implementation' (Protocol in workflow.md)
    - [ ] Agent verification: Automatically run `PYTHONPATH=. CI=true .venv/bin/pytest tests/e2e/` in headless Chromium
