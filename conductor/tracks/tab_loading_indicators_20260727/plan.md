# Implementation Plan: Tab & Component Loading Indicators

## Phase 1: Helper Utility & Component Wrappers
- [x] Task: Create loading indicator helper utility and unit tests
    - [x] Implement `wrap_with_loading` helper utilizing `dcc.Loading` with `dbc.Spinner` style and `delay_show=500`
    - [x] Write unit tests verifying wrapper structure and DOM ID preservation
- [x] Task: Conductor - User Manual Verification 'Phase 1: Helper Utility & Component Wrappers' (Protocol in workflow.md)
    - [x] Agent verification: Automatically run unit tests `PYTHONPATH=. CI=true .venv/bin/pytest tests/`

## Phase 2: Tab View Integration
- [x] Task: Wrap heavy components in Personal Stash and Analytics views
    - [x] Integrate loading wrappers into Personal Stash grid and Analytics Plotly chart components
- [x] Task: Wrap heavy components in Search views
    - [x] Integrate loading wrappers into Pattern Search and Yarn Search results containers
- [x] Task: Conductor - User Manual Verification 'Phase 2: Tab View Integration' (Protocol in workflow.md)
    - [x] Agent verification: Automatically run Playwright E2E browser tests verifying spinner DOM elements during callback delays
