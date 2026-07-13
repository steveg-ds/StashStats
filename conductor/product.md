# Product Guide: StashStats

## Overview
StashStats is a Dash-based web application designed to help yarn enthusiasts search, track, and manage their personal yarn stash. The project focuses on building the `stashies` directory into a robust, comprehensive, reusable Python package for interacting with the Ravelry API, addressing gaps in existing packages (such as the R package `ravelRy`).

## Target Audience
- **Yarn Enthusiasts**: Users who want to visualize, track, and analyze details of their yarn stash (brands, colors, fiber compositions, and weights).
- **Ravelry Active Users**: Users who want a convenient interface to manage their local inventory and seamlessly synchronize stash data back and forth with Ravelry.
- **Python Developers**: Developers looking for a clean, comprehensive Python package (`stashies`) to interact with the Ravelry API.

## Core Features
1. **Ravelry API Python Client**:
   - Reusable Python client library within `stashies` wrapping Ravelry API endpoints.
   - Comprehensive coverage of Ravelry endpoints (yarns, patterns, stashes, etc.).
2. **Stash Analytics**:
   - Visual charts displaying distributions of yarn weights, fiber types, color families, and brands.
   - Interactive filtering to analyze specific categories of the stash.
3. **Inventory Management**:
   - Keep track of original purchase values (yards, meters, skeins, grams) versus remaining amounts.
   - Log history events with specific dates when yarn is used in projects.
4. **Search & Cache**:
   - Query patterns and yarns via the Ravelry API.
   - Local-first cache using SQLite to ensure fast performance and query resilience.

## Ravelry API Integration
- **Bi-directional Sync**: Edits made to yarn quantities, notes, or usage dates in the StashStats interface sync back to the user's Ravelry account to maintain consistency.

## UI/UX Design
- **Visual Cards**: A rich grid layout utilizing customizable cards to display each stash entry.
- **Card Content**: Each card features yarn photo thumbnails, remaining progress bars, and key metadata (fiber, color, weight).
- **Responsive Layout**: Designed for seamless viewing across multiple device viewports.
