# Add Standard GitHub Repository Files via Jules Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add standard GitHub community files, templates, dependencies list, and CI configuration to the repository using a Jules task.

**Architecture:** A Jules task will be started with a detailed instruction set. Jules will read the existing `StashStats.md` and repository setup to generate appropriate repository standards without affecting Obsidian files.

**Tech Stack:** GitHub Actions, Python, Pytest, Markdown.

---

### Task 1: Trigger Jules Task for Standard GitHub Repository Files

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`
- Create: `CODE_OF_CONDUCT.md`
- Create: `SECURITY.md`
- Create: `requirements.txt`
- Create: `.github/pull_request_template.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Run start_new_jules_task tool**

  Run the lazy MCP tool `julesServer/start_new_jules_task` with the parameters:
  - **repo_name**: `"steveg-ds/StashStats"`
  - **user_task_description**:
    ```text
    Read StashStats.md to understand the codebase. Add standard GitHub repository files without deleting or modifying StashStats.md:
    1. Replace the dummy README.md in the root directory. Write a comprehensive, polished, professional README.md with project overview, features, directory layout, installation steps, and testing guide.
    2. Add requirements.txt to the root directory with dependencies extracted from StashStats.md setup instructions.
    3. Add a LICENSE file (MIT License).
    4. Add CONTRIBUTING.md for contribution guidelines.
    5. Add CODE_OF_CONDUCT.md (Contributor Covenant).
    6. Add SECURITY.md detailing security reporting policies.
    7. Add GitHub Actions CI workflow in .github/workflows/ci.yml to run pytest on pull requests and pushes to main. Ensure Playwright browser installation is handled in the workflow.
    8. Add .github/pull_request_template.md.
    9. Add .github/ISSUE_TEMPLATE/bug_report.md and .github/ISSUE_TEMPLATE/feature_request.md.
    Ensure all files follow professional repository standards and contain clean, valid markdown. Do not modify StashStats.md.
    ```

- [ ] **Step 2: Verify task initialization**
  Verify that the Jules task has successfully started and received the instruction payload.
