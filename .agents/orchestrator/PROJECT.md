# Project: StashStats Refactoring

## Architecture
- `app.py`: Dash frontend layout and callback wiring.
- `stashies/db.py`: SQLite database manager with WAL enabled (replacing psycopg2).
- `stashies/model.py`: Core Ravelry API wrapper and Redis cache coordination.
- `stashies/app_controller.py`: Controller mapping API results to UI objects.
- `stashies/components/search_results.py`: UI search result forms including new date-picker.
- `stashies/components/edit_modal.py`: Modal form for log usage, including new date-picker.

## Code Layout
- `app.py`
- `stashies/`
  - `db.py`
  - `model.py`
  - `app_controller.py`
  - `components/`
    - `search_results.py`
    - `edit_modal.py`
- `tests/`
  - `test_e2e.py`

## Milestones
| # | Name | Scope | Dependencies | Status | Conv ID |
|---|------|-------|-------------|--------|---------|
| 1 | Infrastructure & DB | SQLite rewrite of db.py, Dockerfile, docker-compose, requirements, .env.example, component layout | None | IN_PROGRESS | bb42c1c7-bce9-47ec-ba82-61ddf734a9b2 |
| 2 | Model Caching | Update model.py with SQLite support & Redis cache logic | M1 | PLANNED | |
| 3 | App & Integration | Wire everything in app.py & app_controller.py, add callbacks, fix analytics tab, debounce input | M1, M2 | PLANNED | |
| 4 | Final Verification | E2E and adversarial testing validation | M3 | IN_PROGRESS | 62dfae8b-f345-49cf-8e01-87185ce822af |

## Interface Contracts
### DB Manager (`stashies/db.py`)
- `get_original_values(stash_id: int) -> Optional[dict]`
- `save_original_values(stash_id: int, yards: float, meters: float, skeins: float, grams: float) -> None`
- `get_stash_history(stash_id: int) -> List[dict]`
- `save_history_event(stash_id: int, event_date: str, yards: float, meters: float, skeins: float, grams: float) -> None`
