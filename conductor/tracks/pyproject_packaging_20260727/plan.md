# Implementation Plan: Reproducible Packaging with pyproject.toml and uv

## Phase 1: PEP 621 pyproject.toml & Editable Package Setup
- [x] Task: Create pyproject.toml and editable build configuration
    - [x] Write package resolution test verifying `import stashies` works without `PYTHONPATH` (TDD Red phase)
    - [x] Create `pyproject.toml` with PEP 621 metadata, `setuptools` build backend, and dependencies
    - [x] Install package in editable mode (`.venv/bin/pip install -e .` / `uv pip install -e .`)
- [x] Task: Conductor - User Manual Verification 'Phase 1: PEP 621 pyproject.toml & Editable Package Setup' (Protocol in workflow.md)
    - [x] Agent verification: Automatically verify `.venv/bin/python -c "import stashies"` succeeds without `PYTHONPATH`

## Phase 2: Lockfile Generation & Docker Integration
- [x] Task: Generate uv lockfile and update documentation/Dockerfile
    - [x] Generate `uv.lock` using `uv lock` / `uv pip compile`
    - [x] Update `Dockerfile` to use `pyproject.toml` and `uv` for reproducible builds
    - [x] Verify test suite passes with new package layout
- [x] Task: Conductor - User Manual Verification 'Phase 2: Lockfile Generation & Docker Integration' (Protocol in workflow.md)
    - [x] Agent verification: Automatically execute full test suite `CI=true .venv/bin/pytest tests/`
