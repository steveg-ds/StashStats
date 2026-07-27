# Specification: Additional Ravelry API Endpoints in Stashies Client

## Overview
Expand the `stashies` Python client library by implementing low-hanging fruit Ravelry API endpoints (`queue`, `favorites`, `color_families`, `yarn_weights`) as modular client classes integrated into the unified `RavelryClient` facade.

## Functional Requirements
- **Client Modules**:
  - `QueueClient` (`stashies/client/queue.py`): Implement `get_queue(username)` querying `/people/{username}/queue/list.json`.
  - `FavoritesClient` (`stashies/client/favorites.py`): Implement `get_favorites(username)` querying `/people/{username}/favorites/list.json`.
  - `ColorFamiliesClient` (`stashies/client/color_families.py`): Implement `get_color_families()` querying `/color_families.json`.
  - `YarnWeightsClient` (`stashies/client/yarn_weights.py`): Implement `get_yarn_weights()` querying `/yarn_weights.json`.
- **Facade Integration**:
  - Inherit and expose all new client methods on the main `RavelryClient` facade class in `stashies/client/__init__.py`.
- **Testing**:
  - Comprehensive unit tests (`tests/test_ravelry_client_queue.py`, `tests/test_ravelry_client_favorites.py`, etc.) using `unittest.mock`.
  - Integration test skeletons for running against live endpoints.

## Acceptance Criteria
- All 4 new client modules are implemented, type-annotated, and exposed on `RavelryClient`.
- Pytest suite runs and passes cleanly for all new client endpoints.
