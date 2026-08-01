# Implementation Plan: Temperature Blanket Tracking, Ravelry Linkage & Stash Mapping

## Phase 1: Open-Meteo Weather Client & Database Schemas [checkpoint: 0ad5895]
- [x] Task: Implement Open-Meteo Weather API Client [acfcd63]
    - [x] Create `stashies/weather_client.py` wrapping Open-Meteo archive API supporting °F/°C and Mean/High/Low temp metrics
    - [x] Write unit tests verifying daily temp JSON parsing and caching
- [x] Task: Temperature Blanket Database Schema Extensions [30f4913]
    - [x] Add `temperature_projects`, `temperature_palette_mapping`, and `temperature_daily_logs` tables in `stashies/db.py`
    - [x] Implement `DBManager` helper classmethods for project CRUD operations
    - [x] Write unit tests verifying schema creation and DBManager queries
- [x] Task: Conductor - User Manual Verification 'Phase 1: Open-Meteo Weather Client & Database Schemas' (Protocol in workflow.md) [0ad5895]

## Phase 2: Create Temperature Blanket Modal & Configuration Wizard [checkpoint: 166f9c5]
- [x] Task: Implement Multi-Step Temperature Blanket Creation Modal [68a351b]
    - [x] Create `stashies/components/temperature_modal.py` with 5 wizard steps (Location/Dates -> Metric/Units -> Tiers -> Stash/New Yarns -> Ravelry Link)
    - [x] Implement yardage requirement calculator comparing against `DBManager` stash totals
    - [x] Write unit tests for wizard step callbacks and yardage calculations
- [x] Task: Ravelry Project Creation & Stash Linking [2fbae4f]
    - [x] Implement Ravelry project POST helper in `Model` / `RavelryClient` linking stash yarn packs
    - [x] Write unit tests mocking Ravelry API responses
- [x] Task: Conductor - User Manual Verification 'Phase 2: Create Temperature Blanket Modal & Configuration Wizard' (Protocol in workflow.md) [166f9c5]

## Phase 3: Dash UI Tab & 365-Day Grid Visualization
- [ ] Task: Implement Temperature Blanket Tab Layout & 365-Day Row Grid
    - [ ] Create `stashies/components/temperature_blanket.py` with row-by-row color grid and temperature legend
    - [ ] Add `Temperature Blanket` tab (`tab-temperature-blanket`) to `AppController` and `app.py`
    - [ ] Implement row completion checkboxes and stash usage logging callbacks
    - [ ] Write Playwright E2E browser tests verifying grid renders, modal flow, and row log checkboxes
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Dash UI Tab & 365-Day Grid Visualization' (Protocol in workflow.md)
