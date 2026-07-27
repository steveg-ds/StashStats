# Specification: Tab & Component Loading Indicators

## Overview
Implement responsive loading indicators using Dash Bootstrap Components (`dbc.Spinner` / `dcc.Loading`) for heavy computing elements across tabs (Personal Stash grid, Stash Analytics charts, Ravelry API searches) to provide immediate visual feedback during long-running operations.

## Functional Requirements
- **Component Wrapping**:
  - Wrap slow components individually (Stash grid cards, Analytics Plotly charts, Search results container) using `dcc.Loading` configured with `dbc.Spinner` styling.
- **Timing & Performance**:
  - Configure loading indicators with a slight delay (`delay_show` e.g., 500ms) to avoid flickering on fast queries while providing feedback on slow operations.
- **Tab Integration**:
  - Integrate loaders into Personal Stash, Stash Analytics, Pattern Search, and Yarn Search tab views without disrupting Dash grid/flexbox layouts.

## Acceptance Criteria
- Loading spinners show cleanly when switching tabs or triggering heavy callbacks.
- Dash callbacks execute and update components without interference from spinner wrappers.
- Layout remains responsive across all viewports.
