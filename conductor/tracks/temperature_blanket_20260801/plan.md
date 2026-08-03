# Implementation Plan: Temperature Blanket Tracking, Ravelry Linkage & Stash Mapping

## Phase 1: Open-Meteo Weather Client & Database Schemas
- [ ] Task: Implement Open-Meteo Weather API Client
    - [ ] Create `stashies/weather_client.py` wrapping Open-Meteo archive API supporting °F/°C and Mean/High/Low temp metrics
    - [ ] Write unit tests verifying daily temp JSON parsing and caching
- [ ] Task: Temperature Blanket Database Schema Extensions
    - [ ] Add `temperature_projects`, `temperature_palette_mapping`, and `temperature_daily_logs` tables in `stashies/db.py`
    - [ ] Implement `DBManager` helper classmethods for project CRUD operations
    - [ ] Write unit tests verifying schema creation and DBManager queries
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Open-Meteo Weather Client & Database Schemas' (Protocol in workflow.md)

## Phase 2: Create Temperature Blanket Modal & Configuration Wizard
- [ ] Task: Implement Multi-Step Temperature Blanket Creation Modal
    - [ ] Create `stashies/components/temperature_modal.py` with 5 wizard steps (Location/Dates -> Metric/Units -> Tiers -> Stash/New Yarns -> Ravelry Link)
    - [ ] Implement yardage requirement calculator comparing against `DBManager` stash totals
    - [ ] Write unit tests for wizard step callbacks and yardage calculations
- [ ] Task: Ravelry Project Creation & Stash Linking
    - [ ] Implement Ravelry project POST helper in `Model` / `RavelryClient` linking stash yarn packs
    - [ ] Write unit tests mocking Ravelry API responses
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Create Temperature Blanket Modal & Configuration Wizard' (Protocol in workflow.md)

## Phase 3: Dash UI Tab & 365-Day Grid Visualization
- [ ] Task: Implement Temperature Blanket Tab Layout & 365-Day Row Grid
    - [ ] Create `stashies/components/temperature_blanket.py` with row-by-row color grid and temperature legend
    - [ ] Add `Temperature Blanket` tab (`tab-temperature-blanket`) to `AppController` and `app.py`
    - [ ] Implement row completion checkboxes and stash usage logging callbacks
    - [ ] Write Playwright E2E browser tests verifying grid renders, modal flow, and row log checkboxes
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Dash UI Tab & 365-Day Grid Visualization' (Protocol in workflow.md)
