# Implementation Plan: Build comprehensive Ravelry API Python client in stashies

## Phase 0: Workspace Setup & Audit

- [ ] Task: Initialize isolated development workspace
    - [ ] Create a git worktree for this track to isolate work on the client package
- [ ] Task: Audit existing Ravelry API implementation
    - [ ] Review `stashies/base_req.py` and `stashies/model.py` to identify existing API calls, authentication patterns, and caching mechanics to maximize reuse and maintain compatibility

## Phase 0.5: Delegation & Multi-Agent Orchestration Plan

- [ ] Task: Design delegation and orchestration strategy
    - [ ] Map out specific tasks (e.g., model creation, specific endpoints) to delegate to subagents (e.g., `cavecrew-builder` or specialized workers)
    - [ ] Define integration interfaces and validation protocols for coordinated subagent merges

## Phase 1: Client Foundation & Authentication

- [ ] Task: Setup Ravelry HTTP request client structure and auth
    - [ ] Write unit tests for Ravelry Client initialization, API request headers, and authentication validation
    - [ ] Implement `RavelryClient` class with basic HTTP request wrappers and error/retry logic in `stashies/ravelry_client.py`
- [ ] Task: Implement Ravelry data models
    - [ ] Write unit tests verifying JSON parsing and serialization of Ravelry API responses for yarns and patterns
    - [ ] Define Ravelry API Pydantic/dataclass models in `stashies/dataclasses/`
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Client Foundation & Authentication' (Protocol in workflow.md)

## Phase 2: Core Endpoints Implementation

- [ ] Task: Implement Yarn search and details endpoints
    - [ ] Write unit tests for RavelryClient search_yarn and get_yarn methods (mocking Ravelry API responses)
    - [ ] Implement `search_yarn` and `get_yarn` endpoint wrappers in `RavelryClient`
- [ ] Task: Implement Pattern search and details endpoints
    - [ ] Write unit tests for RavelryClient search_patterns and get_pattern methods
    - [ ] Implement `search_patterns` and `get_pattern` endpoint wrappers in `RavelryClient`
- [ ] Task: Implement User Stash endpoints and modification
    - [ ] Write unit tests for fetching user stash entries, adding new stash items, and updating quantities
    - [ ] Implement user stash retrieval and update endpoints in `RavelryClient`
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Core Endpoints Implementation' (Protocol in workflow.md)

## Phase 3: Controller Integration & Local Sync

- [ ] Task: Integrate new RavelryClient with AppController
    - [ ] Write unit tests verifying AppController interacts with the new client structure instead of raw requests
    - [ ] Refactor `stashies/app_controller.py` to use `RavelryClient` for search and details retrieval
- [ ] Task: Align local caching and database logic with new models
    - [ ] Write unit tests for caching RavelryClient model responses in local DB
    - [ ] Refactor `stashies/db.py` to align with the new data models and cache format
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Controller Integration & Local Sync' (Protocol in workflow.md)
