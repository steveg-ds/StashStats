# Implementation Plan: Additional Ravelry API Endpoints in Stashies Client

## Phase 1: Notebook Endpoints (Queue & Favorites)
- [x] Task: Implement Queue & Favorites client classes
    - [x] Write unit tests for `QueueClient` and `FavoritesClient` (TDD Red phase)
    - [x] Create `stashies/client/queue.py` and `stashies/client/favorites.py`
    - [x] Expose `get_queue` and `get_favorites` on `RavelryClient` facade
- [x] Task: Conductor - User Manual Verification 'Phase 1: Notebook Endpoints (Queue & Favorites)' (Protocol in workflow.md)
    - [x] Agent verification: Automatically run `PYTHONPATH=. CI=true .venv/bin/pytest tests/test_ravelry_client_queue.py tests/test_ravelry_client_favorites.py`

## Phase 2: Metadata Endpoints (Color Families & Yarn Weights)
- [x] Task: Implement Color Families & Yarn Weights client classes
    - [x] Write unit tests for `ColorFamiliesClient` and `YarnWeightsClient` (TDD Red phase)
    - [x] Create `stashies/client/color_families.py` and `stashies/client/yarn_weights.py`
    - [x] Expose `get_color_families` and `get_yarn_weights` on `RavelryClient` facade and verify test suite
- [x] Task: Conductor - User Manual Verification 'Phase 2: Metadata Endpoints (Color Families & Yarn Weights)' (Protocol in workflow.md)
    - [x] Agent verification: Automatically run full pytest test suite `PYTHONPATH=. CI=true .venv/bin/pytest tests/`
