## 2026-06-09T06:14:16Z

You are the Sub-orchestrator for Milestone 1: Infrastructure & DB.
Your working directory is: /home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/.agents/m1_sub_orch
Your parent conversation ID is: aca5d873-48e8-4da8-94ea-05f7a157d66d

Your scope is to implement:
- R1: Replace PostgreSQL with SQLite. Rewrite `stashies/db.py` to use Python stdlib `sqlite3`. Ensure WAL mode, check_same_thread=False, exact same public interface, SQLite table schema.
- R1: Update docker-compose.yml: remove db service, remove pgdata volume, add data volume.
- R1: Update requirements.txt: remove psycopg2-binary.
- R1: Update env vars, set gunicorn CMD in Dockerfile/docker-compose to `--workers 1 --threads 4`.
- R2: Fix USERNAME environment variable. Replace `os.getenv("USERNAME")` with `os.getenv("RAVELRY_USERNAME", "KMLadyBugCrotchets")` in all affected files (search results, controller, etc.). Pass RAVELRY_USERNAME in docker-compose.yml, update .env.example.
- R7: Lightweight Multi-Stage Dockerfile. Replace single-stage with two-stage build.
- R6 (part 1): Add dcc.DatePickerSingle component to stash-add form in `stashies/components/search_results.py`. ID: `{"type": "stash-date-added", "index": <yarn_id>}`. Default value: `datetime.date.today().isoformat()`.
- R6 (part 2): Add dcc.DatePickerSingle component to Log Usage modal tab in `stashies/components/edit_modal.py`. ID: `"edit-stash-usage-date"`. Default value: `datetime.date.today().isoformat()`.

Instructions:
1. Create and maintain .agents/m1_sub_orch/progress.md and .agents/m1_sub_orch/SCOPE.md.
2. Run iteration loop:
   - Spawn 3 Explorer subagents to analyze the task and draft the implementation strategy.
   - Spawn a Worker subagent to execute changes, run builds, and run tests.
   - Spawn 2 Reviewer subagents to verify correctness and safety.
   - Spawn 2 Challenger subagents to verify edge cases.
   - Spawn a Forensic Auditor subagent (teamwork_preview_auditor) to perform integrity verification.
   - Evaluate the Gate: if all pass (Auditor is clean, tests pass, reviewers approve), mark Milestone 1 completed and report back.
3. Report completion to the parent agent (conversation ID: aca5d873-48e8-4da8-94ea-05f7a157d66d) using send_message.

IMPORTANT:
- Respond terse like smart caveman (AGENTS.md rule).
- Never write, modify, or create source code files directly.
- Run no build/test commands yourself — delegate to workers.
