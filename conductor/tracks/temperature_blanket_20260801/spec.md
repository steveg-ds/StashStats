# Track Specification: Temperature Blanket Tracking, Ravelry Project Linkage & Stash Mapping

## Overview
Implement a Temperature Blanket Builder & Tracker in StashStats. This feature allows yarn crafters to design 365-day temperature blankets by fetching historical weather data (via Open-Meteo API), configuring temperature metrics and intervals, mapping intervals to existing Ravelry yarn stash entries OR specifying new yarns, calculating yardage requirements against available inventory, creating a linked Ravelry Project, and logging daily row completions.

---

## 1. Functional Requirements

### 1.1 Weather Data Integration (`stashies/weather_client.py`)
- Query historical daily temperatures (high, low, mean) by location (City/Zip or Lat/Lon) and date range via Open-Meteo API (`https://archive-api.open-meteo.com/v1/archive`).
- Support temperature unit selection (°F or °C).
- Cache historical weather query results in local DB (`temperature_weather_cache` table) to prevent redundant API calls.

### 1.2 Interactive "Create Temperature Blanket Project" Modal Workflow
- **Step 1: Location & Date Range:** Location string (City/Zip or Lat/Lon), Start Date (`YYYY-MM-DD`), End Date (`YYYY-MM-DD`).
- **Step 2: Weather Fetch & Metric Selection:**
  - Select Metric: Daily Mean / Average (Standard Default), Daily High, Daily Low, or High/Low Dual-Row Stripe (730 rows/year).
  - Select Units: Fahrenheit (°F) or Celsius (°C).
  - Displays temperature summary (Min, Max, Median) and distribution histogram.
- **Step 3: Interval & Tier Configuration:**
  - Interval Stepping: Equal 5°F/2.5°C, Equal 10°F/5°C, or Custom thresholds.
  - Generates $K$ temperature color tiers.
- **Step 4: Yarn Assignment & Yardage Calibration (Stash Yarn OR New Yarn):**
  - For each temperature tier, user can choose:
    - **Option A:** Select an existing Ravelry stash yarn entry (`stash_id`).
    - **Option B:** Specify a **New Yarn** (yarn name, brand, colorway, hex color, and skein length).
  - Pattern Gauge: Configure estimated row yardage $y_{\text{row}}$ and safety buffer (10%-15%).
  - Yardage Calculator: Computes total tier yardage $Y_k = R_k \cdot y_{\text{row}} \cdot \text{rows\_per\_day}$ and compares against available stash/new yarn yardage.
- **Step 5: Ravelry Project Linkage & Creation:**
  - Calls Ravelry API (`/projects/{username}/create.json`) to create a new Ravelry Project with craft type, notes, and attached yarn packs referencing selected `stash_id` or newly created stash items.
  - Persists project configuration locally in `temperature_projects`.

### 1.3 Dash UI Component & Grid Visualization (`stashies/components/temperature_blanket.py`)
- Integrated as a dedicated top-level tab (`tab-temperature-blanket`).
- **365-Day Color Grid:** Visual row-by-row grid representation of the blanket showing each day's assigned yarn colorway.
- **Temperature Color Legend:** Interactive color gauge showing temperature bounds and corresponding stash/new yarn names.
- **Row Completion Tracker:** Interactive row checkboxes allowing crafters to log completed rows and record stash yardage usage in `stash_history`.

---

## 2. Technical & Database Specifications

### 2.1 Database Schema Extensions (`stashies/db.py`)
- `temperature_projects`:
  - `id SERIAL PRIMARY KEY`
  - `name VARCHAR(255) NOT NULL`
  - `ravelry_project_id VARCHAR(50)`
  - `location VARCHAR(255) NOT NULL`
  - `lat DOUBLE PRECISION NOT NULL`
  - `lon DOUBLE PRECISION NOT NULL`
  - `start_date DATE NOT NULL`
  - `end_date DATE NOT NULL`
  - `temp_metric VARCHAR(20) DEFAULT 'mean'`
  - `units VARCHAR(10) DEFAULT 'F'`
  - `created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP`
- `temperature_palette_mapping`:
  - `id SERIAL PRIMARY KEY`
  - `project_id INTEGER REFERENCES temperature_projects(id) ON DELETE CASCADE`
  - `min_temp DOUBLE PRECISION NOT NULL`
  - `max_temp DOUBLE PRECISION NOT NULL`
  - `stash_id VARCHAR(50)` -- Nullable if new yarn
  - `new_yarn_name VARCHAR(255)` -- Set if new yarn
  - `hex_color VARCHAR(10)`
- `temperature_daily_logs`:
  - `id SERIAL PRIMARY KEY`
  - `project_id INTEGER REFERENCES temperature_projects(id) ON DELETE CASCADE`
  - `log_date DATE NOT NULL`
  - `temperature DOUBLE PRECISION NOT NULL`
  - `is_completed BOOLEAN DEFAULT FALSE`

---

## 3. Acceptance Criteria
- [ ] Users can query historical weather data globally via Open-Meteo without requiring an API key.
- [ ] Users can select either existing Ravelry stash yarns OR define new yarns when building color palettes.
- [ ] Users can configure temp metric (Mean default, High, Low, Dual Stripe), °F/°C units, and interval stepping modes.
- [ ] Users can map temperature tiers to yarns and compare required vs available yardage.
- [ ] Users can create a Ravelry Project directly from the wizard, linking stash yarn packs.
- [ ] The Dash UI displays a 365-day color grid, temperature legend, and interactive row completion logger.
- [ ] Full test coverage (>80%) with pytest unit tests and Playwright E2E browser tests.
