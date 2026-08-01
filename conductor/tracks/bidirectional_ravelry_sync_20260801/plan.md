# Implementation Plan: Bi-Directional Ravelry Batch Sync & Unsynced Change Tracking

## Phase 1: Pydantic Sync State Model & Database Schema Extensions
- [ ] Task: Implement Pydantic V2 StashSyncState model
    - [ ] Create `stashies/dataclasses/stash_sync_state.py` with Pydantic V2 validation
    - [ ] Write unit tests verifying model validation and default values
- [ ] Task: Database Schema & DBManager Extensions
    - [ ] Add `stash_sync_state` table to DBManager migrations
    - [ ] Implement `mark_dirty`, `get_dirty_stash_ids`, `get_sync_state`, `mark_synced`, and `get_unsynced_count` in `DBManager`
    - [ ] Write unit tests verifying DBManager sync state tracking
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Pydantic Sync State Model & Database Schema Extensions' (Protocol in workflow.md)

## Phase 2: Batch Sync Engine & UI Change Tracking
- [ ] Task: AppController Batch Sync Engine & Stash Card Badges
    - [ ] Implement `execute_batch_sync` in `AppController`
    - [ ] Add `Pending Sync` badge logic to `StashCard` and accordion items
    - [ ] Write unit tests mocking Ravelry API calls for sync execution
- [ ] Task: Personal Stash Sync Button & E2E Integration
    - [ ] Add "Sync Now" button, pending badge, and callback to Dash app
    - [ ] Implement 24-hour background sync scheduler
    - [ ] Write Playwright E2E browser tests verifying sync button, badge updates, and loading indicators
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Batch Sync Engine & UI Change Tracking' (Protocol in workflow.md)
