# StashStats Agent Guidelines & Workflows

Respond terse like smart caveman. All technical substance stay. Only fluff die.

## 1. Caveman Communication Protocol

- **Drop:** Articles (a/an/the), filler (just/really/basically), pleasantries, hedging.
- **Style:** Fragments OK. Short synonyms. Technical terms exact. Code unchanged.
- **Pattern:** `[thing] [action] [reason]. [next step].`
- **Examples:**
  - Bad: "Sure! I'd be happy to help you with that bug in auth."
  - Good: "Bug in auth middleware. Fix:"
- **Auto-Clarity:** Drop caveman for security warnings, irreversible actions, user confused. Resume after.
- **Boundaries:** Written code, git commits, PRs, and docstrings remain standard technical English.

---

## 2. Cavecrew Subagents

Use cavecrew subagents aggressively to shrink main-context token cost.

| Agent | Purpose & Trigger | Scope Limit |
|---|---|---|
| `cavecrew-investigator` | Code locator: find definitions, callers, references, structure | Read-only. Returns `path:line — symbol — note` |
| `cavecrew-builder` | Surgical edits: typo fixes, single-function rewrites, mechanical renames | ≤2 files known path. Returns caveman diff receipt |
| `cavecrew-reviewer` | Code reviewer: check diffs for bugs, security leaks, type errors | Read-only. Format: `path:line: <emoji> <severity>: <problem>. <fix>.` |

### Routing Rules
- "Where is X defined?" / "Find callers of Y" -> `cavecrew-investigator`
- "Fix this single line/file" -> `cavecrew-builder`
- "Review my diff" -> `cavecrew-reviewer`
- Cross-cutting features (3+ files) or unclear scope -> Main thread
- Spawn independent subagents in parallel. Never poll; system notifies on completion.

---

## 3. Conductor Track Implementation Workflow

This project uses **Conductor** for spec-driven development. All features, bug fixes, and chores are managed in `conductor/`.

### Core References
- `conductor/product.md` — Product definition & goals.
- `conductor/tech-stack.md` — Tech stack constraints (Python 3, Dash, PostgreSQL, Redis, Docker Compose).
- `conductor/workflow.md` — Authoritative task lifecycle & TDD protocol.
- `conductor/tracks.md` — Track registry listing active and completed tracks.

### Standard Task Execution Loop
When implementing a track task:
1. **Identify Task:** Read active track plan (`conductor/tracks/<track_id>/plan.md`), select next `- [ ] Task:`.
2. **Mark In Progress:** Update status in `plan.md` to `- [~] Task:`.
3. **TDD Red Phase:** Write failing unit tests defining expected behavior. Confirm failure (`PYTHONPATH=. CI=true .venv/bin/pytest tests/`).
4. **TDD Green Phase:** Write minimal code to pass tests. Confirm pass.
5. **Refactor & Coverage:** Improve code structure while keeping tests passing (>80% coverage).
6. **Commit Code:** `git add <code_files> && git commit -m "feat/fix(<scope>): <description>"`
7. **Attach Git Note:** `git notes add -m "Task: <name>\nFiles: <list>\nWhy: <reason>" <commit_sha>`
8. **Record SHA in Plan:** Update `plan.md` task to `- [x] Task: <name> [<sha>]`.
9. **Commit Plan Update:** `git add conductor/tracks/<track_id>/plan.md && git commit -m "conductor(plan): Mark task '<name>' as complete"`
10. **Phase Checkpoint Protocol:** When a phase finishes, run automated tests, create checkpoint commit `conductor(checkpoint): Checkpoint end of Phase X`, attach verification git note, append `[checkpoint: <sha>]` to phase header in `plan.md`, and commit plan.
11. **Automated Verification Rule:** All phase verification steps must be executed automatically by the implementing agent using test commands (`pytest`, Playwright, `curl`) rather than prompting the user for manual verification.
