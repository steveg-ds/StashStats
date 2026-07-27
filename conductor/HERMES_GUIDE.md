# Hermes Agent Guide: Conductor Track Implementation Protocol

This guide is optimized for **Hermes agents** (and any AI coding assistant without native Conductor slash commands or IDE extensions) to implement feature, bugfix, or chore tracks in this repository cleanly, accurately, and deterministically.

---

## 1. Directory Structure Overview

```
conductor/
├── tracks.md                               # Tracks Registry (List of all project tracks)
├── product.md                              # Product Definition & Feature Overview
├── tech-stack.md                           # Tech Stack & Architecture Constraints
├── workflow.md                             # Authoritative Task Lifecycle & Guidelines
├── HERMES_GUIDE.md                         # This implementation guide for external agents
└── tracks/
    └── <track_id>/
        ├── index.md                        # Track context index
        ├── metadata.json                   # Track metadata (type, status, timestamps, hermes_session_id)
        ├── spec.md                         # Feature/bug specification
        └── plan.md                         # Hierarchical task plan
```

---

## 2. Track Discovery & Initialization

To begin implementing a track:

1. **Locate Active Track:**
   - Read `conductor/tracks.md`.
   - Find the first track marked `[~]` (In Progress) or `[ ]` (Pending).
   - Get the link path (e.g. `./tracks/fix_stash_loading_20260727/`).

2. **Load Track Context:**
   - Read `conductor/tracks/<track_id>/spec.md` for requirements.
   - Read `conductor/tracks/<track_id>/plan.md` for task structure.
   - Read `conductor/tech-stack.md` and `conductor/workflow.md` for code & testing rules.

3. **Mark Track In Progress (if `[ ]`):**
   - Edit `conductor/tracks.md` to update status: `- [~] **Track: <Name>**`.
   - Commit update:
     ```bash
     git add conductor/tracks.md
     git commit -m "chore(conductor): Mark track '<Name>' as in progress"
     ```

---

## 3. Step-by-Step Task Implementation Loop

For every task in `conductor/tracks/<track_id>/plan.md`:

### Step 3.1: Select Task & Mark In Progress
- Read `plan.md` and find the first pending task (`- [ ] Task: <Task Description>`).
- Edit `plan.md` to change status to `- [~] Task: <Task Description>`.

### Step 3.2: TDD Red Phase (Write Failing Tests)
- Create or update a test file under `tests/` (e.g. `tests/test_feature.py`).
- Write unit tests covering expected behavior according to `spec.md`.
- Execute test command to verify failure:
  ```bash
  PYTHONPATH=. CI=true .venv/bin/pytest tests/test_feature.py
  ```
- **CRITICAL:** Do NOT write implementation code until tests fail as expected.

### Step 3.3: TDD Green Phase (Implement Code)
- Write the minimum necessary implementation code in `stashies/` or app root.
- Use Hermes subagents (`delegate_task` or `cavecrew-builder`) for surgical edits where appropriate.
- Execute test command to verify all tests pass:
  ```bash
  PYTHONPATH=. CI=true .venv/bin/pytest tests/
  ```

### Step 3.4: Refactor & Code Coverage
- Clean up implementation while ensuring tests continue to pass.
- Verify test coverage (>80% target):
  ```bash
  PYTHONPATH=. CI=true .venv/bin/pytest --cov=stashies tests/
  ```

### Step 3.5: Commit Code Changes
- Stage source and test files (do NOT stage `plan.md` yet):
  ```bash
  git add stashies/ tests/
  git commit -m "feat/fix(<scope>): <concise description of work>"
  ```

### Step 3.6: Attach Git Note to Commit
- Get short commit hash: `git log -1 --format="%h"`
- Attach auditable task summary note:
  ```bash
  git notes add -m "Task: <Task Description>
  Files: <list of files modified>
  Why: <rationale for change>" <commit_hash>
  ```

### Step 3.7: Update Plan & Commit Plan State
- Edit `plan.md`: Change task status to `- [x] Task: <Task Description> [<commit_sha>]`.
- Stage and commit plan:
  ```bash
  git add conductor/tracks/<track_id>/plan.md
  git commit -m "conductor(plan): Mark task '<Task Description>' as complete"
  ```

---

## 4. Phase Completion & Checkpointing Protocol

When you complete all functional tasks in a Phase and reach a verification meta-task:
`- [ ] Task: Conductor - User Manual Verification '<Phase Name>' (Protocol in workflow.md)`

Execute the checkpointing protocol:

1. **Execute Automated Tests:**
   ```bash
   PYTHONPATH=. CI=true .venv/bin/pytest tests/
   ```
2. **Execute Agent Verification Sub-Tasks:**
   - Run any specific verification commands listed under the task in `plan.md`.
3. **Create Empty Checkpoint Commit:**
   ```bash
   git commit --allow-empty -m "conductor(checkpoint): Checkpoint end of <Phase Name>"
   ```
4. **Get Checkpoint SHA:** `git log -1 --format="%h"`
5. **Attach Verification Report Note:**
   ```bash
   git notes add -m "Verification Report: <Phase Name>
   Automated test command: PYTHONPATH=. CI=true .venv/bin/pytest tests/
   Result: Passed" <checkpoint_sha>
   ```
6. **Update `plan.md` Header & Task:**
   - Update phase header: `## Phase X: <Phase Name> [checkpoint: <checkpoint_sha>]`
   - Update verification task: `- [x] Task: Conductor - User Manual Verification '<Phase Name>' (Protocol in workflow.md) [<checkpoint_sha>]`
7. **Commit Plan Update:**
   ```bash
   git add conductor/tracks/<track_id>/plan.md
   git commit -m "conductor(plan): Mark phase '<Phase Name>' as complete"
   ```

---

## 5. Finalizing Track Completion

Once all phases and tasks in `plan.md` are marked `[x]`:

1. **Update Tracks Registry:**
   - Edit `conductor/tracks.md`: Change track status from `[~]` or `[ ]` to `[x]`.
   - Example: `- [x] **Track: <Track Name>**`.
2. **Commit Registry Update:**
   ```bash
   git add conductor/tracks.md
   git commit -m "chore(conductor): Mark track '<Track Name>' as complete"
   ```
3. **Synchronize Product / Tech Stack Docs:**
   - If technical contracts or capabilities changed, update `conductor/product.md` or `conductor/tech-stack.md`.
   - Commit sync: `git commit -m "docs(conductor): Synchronize docs for track '<Track Name>'"`

---

## 6. Session Tracking, Goals & AGY Review Loop

### 6.1 Session ID Tracking in `metadata.json`
To allow seamless multi-turn conversation resumption across task iterations:
1. When AGY initializes Hermes for a track, AGY passes `--pass-session-id` and stores `hermes_session_id` in `conductor/tracks/<track_id>/metadata.json`:
   ```json
   {
     "track_id": "<track_id>",
     "type": "feature",
     "status": "in_progress",
     "hermes_session_id": "<session_id>"
   }
   ```
2. Subsequent calls use `--resume <session_id>`:
   ```bash
   hermes chat -m openrouter/free --resume <session_id> -q "Implement next task in track <track_id>"
   ```

### 6.2 Autonomous Goal Mode (`/goal` & `/subgoal`)
When dispatching complex multi-step tasks, AGY passes `/goal` to Hermes to enable autonomous iterative execution across turns:
```bash
hermes chat -m openrouter/free --resume <session_id> -q "/goal Implement task '<Task Name>' cleanly with TDD. Keep working until all unit tests pass, git note is attached, and plan.md is updated."
```
Hermes will use its native goal engine to track progress, execute subgoals, and iterate until the criteria are satisfied.

### 6.3 Subagent Delegation Strategy
When implementing tasks with `openrouter/free`, Hermes SHOULD use `delegate_task` or local subagents (`cavecrew-builder`) for isolated lookups and surgical single-file edits to conserve context and maximize accuracy.

### 6.4 Handling AGY Review Feedback
After Hermes completes a task/goal, Antigravity (AGY) reviews the diff and runs the automated test suite.
If AGY finds bugs, failing assertions, or style issues, AGY resumes the tracked Hermes session with specific fix instructions:
```bash
hermes chat -m openrouter/free --resume <session_id> -q "AGY Review Feedback for '<Task Name>': <Specific error / bug description>. Please fix implementation in <file>, ensure tests pass, and commit updated code."
```
Hermes MUST address the reported issues, verify tests pass (`pytest`), update git commit/notes if necessary, and report back to AGY.
