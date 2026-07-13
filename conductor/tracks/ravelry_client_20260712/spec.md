# Specification: Build comprehensive Ravelry API Python client in stashies

## Goals
- Build a robust, reusable Python package under the `stashies` directory to wrap Ravelry API endpoints.
- Support essential endpoints needed by the UI, including yarns, patterns, user stash lists, and sync edits.
- Use explicit Python typing and docstrings (Strict Pythonic guideline) for class definitions and data models.
- Support offline-first cache operations by modeling API responses so that the local database sync is seamless.

## Architecture
- `stashies/ravelry_client.py`: Core client class. Manages authentication, request headers, error handling, rate limiting, and retries.
- `stashies/dataclasses/`: Strong type representations. Align with Ravelry's JSON responses (e.g. `yarn.py`, `colorway.py`, `yarn_photos.py`).
- Integration points:
  - `stashies/app_controller.py`: Interacts with `RavelryClient` for search and user stash updates.
  - `stashies/db.py`: Cache client responses locally in SQLite (or PostgreSQL in future tracks).

## Security
- API Credentials (username/password/tokens) must be read from environment variables (.env) or system config.
- Never hardcode API keys or credentials.
