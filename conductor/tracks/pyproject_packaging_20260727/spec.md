# Specification: Reproducible Packaging with pyproject.toml and uv

## Overview
Migrate the project dependency and package configuration to a standard PEP 621 `pyproject.toml` file with `setuptools` build backend, `uv` package management, and `uv.lock` determinism to prevent virtual environment corruption and module resolution failures.

## Functional Requirements
- **PEP 621 `pyproject.toml` Configuration**:
  - Define project metadata, dependencies (Dash, DBC, Pydantic, psycopg2-binary, redis, pytest, playwright, etc.), and optional dev dependencies.
  - Configure `setuptools` build backend with package discovery for `stashies`.
- **Editable Package Installation**:
  - Configure `stashies` as an editable package so `import stashies` resolves natively inside `.venv` without needing manual `PYTHONPATH=.` overrides.
- **`uv` Integration & Deterministic Locking**:
  - Generate `uv.lock` using `uv lock` / `uv pip compile`.
  - Update developer setup & Dockerfile commands to use `uv sync` / `uv pip install` for instant, repeatable environment instantiation.

## Acceptance Criteria
- `pyproject.toml` created with complete PEP 621 metadata and dependency list.
- `uv pip install -e .` (or `uv sync`) installs `stashies` in editable mode cleanly inside `.venv`.
- `python -c "import stashies"` succeeds without setting `PYTHONPATH`.
- All pytest unit and E2E tests pass cleanly.
