# Implementation Plan: Build comprehensive Ravelry API Python client in stashies

## Phase 0: Workspace Setup & Audit

- [x] Task: Initialize isolated development workspace
    - [x] Create a git worktree for this track to isolate work on the client package
- [x] Task: Audit existing Ravelry API implementation
    - [x] Review `stashies/base_req.py` and `stashies/model.py` to identify existing API calls, authentication patterns, and caching mechanics to maximize reuse and maintain compatibility

## Phase 0.5: Delegation & Multi-Agent Orchestration Plan

- [x] Task: Design delegation and orchestration strategy
    - [x] Map out specific tasks (e.g., model creation, specific endpoints) to delegate to subagents (e.g., `cavecrew-builder` or specialized workers)
    - [x] Define integration interfaces and validation protocols for coordinated subagent merges

## Phase 1: Client Foundation & Authentication

- [x] Task: Setup Ravelry HTTP request client structure and auth
    - [x] Write unit tests for Ravelry Client initialization, API request headers, and authentication validation
    - [x] Implement `RavelryClient` class with basic HTTP request wrappers and error/retry logic in `stashies/ravelry_client.py`
- [x] Task: Implement Ravelry data models
    - [x] Write unit tests verifying JSON parsing and serialization of Ravelry API responses for yarns and patterns
    - [x] Define Ravelry API Pydantic/dataclass models in `stashies/dataclasses/`
- [x] Task: Conductor - User Manual Verification 'Phase 1: Client Foundation & Authentication' (Protocol in workflow.md)

## Phase 2: Core Endpoints Implementation

- [x] Task: Implement Yarn search and details endpoints
    - [x] Write unit tests for RavelryClient search_yarn and get_yarn methods (mocking Ravelry API responses)
    - [x] Implement `search_yarn` and `get_yarn` endpoint wrappers in `RavelryClient`
- [x] Task: Implement Pattern search and details endpoints
    - [x] Write unit tests for RavelryClient search_patterns and get_pattern methods
    - [x] Implement `search_patterns` and `get_pattern` endpoint wrappers in `RavelryClient`
- [x] Task: Implement User Stash endpoints and modification
    - [x] Write unit tests for fetching user stash entries, adding new stash items, and updating quantities
    - [x] Implement user stash retrieval and update endpoints in `RavelryClient`
- [x] Task: Conductor - User Manual Verification 'Phase 2: Core Endpoints Implementation' (Protocol in workflow.md)

## Phase 3: Controller Integration & Local Sync

- [x] Task: Integrate new RavelryClient with AppController
    - [x] Write unit tests verifying AppController interacts with the new client structure instead of raw requests
    - [x] Refactor `stashies/app_controller.py` to use `RavelryClient` for search and details retrieval
- [x] Task: Align local caching and database logic with new models
    - [x] Update database schemas, helper functions, and caching handlers to consistently parse and store objects using the new Pydantic dataclasses
- [~] Task: Conductor - User Manual Verification 'Phase 3: Controller Integration & Local Sync' (Protocol in workflow.md)
