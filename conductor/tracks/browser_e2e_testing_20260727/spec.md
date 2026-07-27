# Specification: Comprehensive Playwright E2E Browser Testing Suite

## Overview
Build a comprehensive end-to-end (E2E) browser testing suite using `pytest-playwright` and Chromium to automate full browser testing of all StashStats Dash application functionalities.

## Functional Requirements
- **Test Infrastructure**:
  - Configure `pytest-playwright` for Python using Chromium.
  - Install Fedora Linux dependencies using `playwright install chromium` / `playwright install-deps chromium`.
  - Support execution in both headless mode (for CI/automated runs) and headed mode (for visual debugging).
  - Add pytest fixtures for managing test app server lifecycle and database isolation fixtures.
- **Test Coverage**:
  - **Dashboard & Charts**: Verify Dash layout, Plotly charts rendering, and summary statistics cards.
  - **Search & Filter**: Test pattern/yarn search inputs, debounced search triggers, and interactive filtering.
  - **Inventory Edit & History**: Automate modal interactions, editing stash values, and recording yarn usage events.
  - **Sync & State Management**: Validate bi-directional modal callbacks and persistent database state updates.

## Acceptance Criteria
- All E2E browser tests execute reliably via `pytest tests/e2e/`.
- Tests pass cleanly in both headless and headed execution modes using Chromium.
- Clear error tracebacks and screenshot/video artifacts generated on test failure.
