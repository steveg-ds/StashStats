# Implementation Plan: Reproducible Packaging with pyproject.toml and uv

## Phase 1: PEP 621 pyproject.toml & Editable Package Setup
- [ ] Task: Create pyproject.toml and editable build configuration
    - [ ] Write package resolution test verifying `import stashies` works without `PYTHONPATH` (TDD Red phase)
    - [ ] Create `pyproject.toml` with PEP 621 metadata, `setuptools` build backend, and dependencies
    - [ ] Install package in editable mode (`.venv/bin/pip install -e .` / `uv pip install -e .`)
- [ ] Task: Conductor - User Manual Verification 'Phase 1: PEP 621 pyproject.toml & Editable Package Setup' (Protocol in workflow.md)
    - [ ] Agent verification: Automatically verify `.venv/bin/python -c "import stashies"` succeeds without `PYTHONPATH`

## Phase 2: Lockfile Generation & Docker Integration
- [ ] Task: Generate uv lockfile and update documentation/Dockerfile
    - [ ] Generate `uv.lock` using `uv lock` / `uv pip compile`
    - [ ] Update `Dockerfile` to use `pyproject.toml` and `uv` for reproducible builds
    - [ ] Verify test suite passes with new package layout
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Lockfile Generation & Docker Integration' (Protocol in workflow.md)
    - [ ] Agent verification: Automatically execute full test suite `CI=true .venv/bin/pytest tests/`
