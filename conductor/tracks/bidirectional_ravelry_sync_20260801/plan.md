# Implementation Plan: Bi-Directional Ravelry Batch Sync & Unsynced Change Tracking

## Phase 1: Pydantic Sync State Model & Database Schema Extensions [checkpoint: 10ff2cd]
- [x] Task: Implement Pydantic V2 StashSyncState model [1c4c304]
    - [x] Create `stashies/dataclasses/stash_sync_state.py` with Pydantic V2 validation
    - [x] Write unit tests verifying model validation and default values
- [x] Task: Database Schema & DBManager Extensions [619c32b]
    - [x] Add `stash_sync_state` table to DBManager migrations
    - [x] Implement `mark_dirty`, `get_dirty_stash_ids`, `get_sync_state`, `mark_synced`, and `get_unsynced_count` in `DBManager`
    - [x] Write unit tests verifying DBManager sync state tracking
- [x] Task: Conductor - User Manual Verification 'Phase 1: Pydantic Sync State Model & Database Schema Extensions' (Protocol in workflow.md) [10ff2cd]

## Phase 2: Batch Sync Engine & UI Change Tracking [checkpoint: 1da154c]
- [x] Task: AppController Batch Sync Engine & Stash Card Badges [e372f22]
    - [x] Implement `execute_batch_sync` in `AppController`
    - [x] Add `Pending Sync` badge logic to `StashCard` and accordion items
    - [x] Write unit tests mocking Ravelry API calls for sync execution
- [x] Task: Personal Stash Sync Button & E2E Integration [c422ec4]
    - [x] Add "Sync Now" button, pending badge, and callback to Dash app
    - [x] Implement 24-hour background sync scheduler
    - [x] Write Playwright E2E browser tests verifying sync button, badge updates, and loading indicators
- [x] Task: Conductor - User Manual Verification 'Phase 2: Batch Sync Engine & UI Change Tracking' (Protocol in workflow.md) [1da154c]
