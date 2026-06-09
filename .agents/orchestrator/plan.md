# Plan: StashStats Refactoring

## Objectives
1. Replace PostgreSQL with SQLite.
2. Fix USERNAME environment variable.
3. Fix Analytics Plots prevent_initial_callbacks race.
4. Debounce Stash Filter Input.
5. Cache Uncached API Calls in Redis.
6. Add Date Pickers to search results and log usage modal.
7. Lightweight Multi-Stage Dockerfile.

## Milestone Plan
1. **Milestone 1: Project Setup & Tests Definition** (Create PROJECT.md, TEST_INFRA.md, set up directories)
2. **Milestone 2: Phase 1 Implementation** (Rewrite db.py, update Dockerfile/docker-compose/requirements, update search_results.py and edit_modal.py)
3. **Milestone 3: Phase 2 Implementation** (Update model.py to use SQLite, implement Redis caching)
4. **Milestone 4: Phase 3 Implementation** (Integrate components and data in app_controller.py and app.py, fix Analytics plots, debounce input)
5. **Milestone 5: Verification & E2E Validation** (Run test suites, confirm all requirements met)
