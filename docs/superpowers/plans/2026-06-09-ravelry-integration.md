# [Ravelry Integration] Implementation Plan
> **Agent instruction**: Use `subagent-driven-development` or `executing-plans`.

Goal: Expand StashStats into a Ravelry web UI with projects management, a queue manager, a needle organizer, and a unified yarn/fiber stash view for the configured user (no OAuth 2.0).
Architecture: Direct Ravelry API calls using Basic Auth developer credentials, cached with Redis TTLs to optimize load times.
Tech Stack: Plotly Dash, Redis, SQLite (for local cache metadata), requests.

---

## Proposed Changes

### Component 1: Unified Yarn & Fiber Stash

#### [MODIFY] [stashies/model.py](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/model.py)
- Replace `people/{username}/stash/list.json` with `people/{username}/stash/unified/list.json` to fetch both yarn and fiber stashes.
- Update data parsing to handle unified stash items (fiber has slightly different properties than yarn, e.g. fiber category, weight, preparation).

#### [MODIFY] [stashies/components/stash_card.py](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/components/stash_card.py)
- Adapt the stash card to show either Yarn or Fiber specific details dynamically based on item type.

---

### Component 2: Project Tracker

#### [NEW] [stashies/components/projects.py](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/components/projects.py)
- Renders the Projects tab layout:
  - Project cards (displaying thumbnail, title, status, craft, pattern name, progress bar).
  - Add Project form triggering a modal.

#### [MODIFY] [stashies/model.py](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/model.py)
- Add API wrappers for `projects/list` (GET), `projects/create` (POST), and `projects/update` (PUT).
- Cache project list in Redis (`projects_list:{username}`, TTL 10m).

---

### Component 3: Queue Manager

#### [NEW] [stashies/components/queue.py](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/components/queue.py)
- Renders the Queue tab layout:
  - List of queued projects in priority order.
  - Buttons to reposition or delete items.

#### [MODIFY] [stashies/model.py](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/model.py)
- Add wrappers for Ravelry queue endpoints: `queue/list` (GET), `queue/create` (POST), `queue/reposition` (POST), and `queue/delete` (DELETE).

---

### Component 4: Needle & Hook Organizer

#### [NEW] [stashies/components/needles.py](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/components/needles.py)
- Renders the Needles tab layout:
  - Grouped tables for knitting needles and crochet hooks (showing type, US size, metric size, length, material, and notes).

#### [MODIFY] [stashies/model.py](file:///home/thotsky/.gemini/antigravity/worktrees/StashStats/docker-compose-stack-setup/stashies/model.py)
- Add read wrapper for `needles/list` (GET).
- Cache list in Redis (`needles_list:{username}`, TTL 1 hour).

---

## Verification Plan

### Automated Tests
- Write mock tests in `tests/test_e2e.py` to mock response payloads for unified stash, projects, queue, and needles.
- Run `pytest` to verify.

### Manual Verification
1. Open Stash Stats web app.
2. Toggle "Projects" tab → list of user projects renders.
3. Toggle "Queue" tab → list of queued items renders with reorder controls.
4. Toggle "Needles" tab → knitting/crochet tools list renders.
