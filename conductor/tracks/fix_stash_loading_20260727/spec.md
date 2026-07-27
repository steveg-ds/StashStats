# Specification: Fix Personal Stash and Stash Analytics Loading Failure

## Overview
Investigate and resolve the bug causing Personal Stash and Stash Analytics tabs to display endless loading or a blank layout after the PostgreSQL database migration.

## Functional Requirements
- **Root Cause Diagnosis**:
  - Inspect Dash callback execution, `DBManager` connection pooling, and data fetching queries in `stashies/db.py` and `stashies/model.py`.
  - Fix any SQL query formatting, missing table handles, connection pool acquisition hangs, or type mismatches resulting from the Postgres migration.
- **Data Rendering**:
  - Ensure Personal Stash tab renders user stash cards cleanly from PostgreSQL/Ravelry data.
  - Ensure Stash Analytics tab calculates and renders Plotly figures without callback failures.

## Acceptance Criteria
- Personal Stash and Stash Analytics tabs load promptly and accurately without endless loading or layout freezes.
- All Dash callbacks execute cleanly with zero database exceptions in backend logs.
- Unit and E2E regression tests pass cleanly.
