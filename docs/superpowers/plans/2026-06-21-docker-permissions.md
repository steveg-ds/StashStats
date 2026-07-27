# Docker Compose Permissions Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Redo Docker Compose configuration to use host UID/GID mapping and SELinux volume flags, resolving file permission issues on Fedora.

**Architecture:** Add UID/GID variables to `.env` and `.env.example`. Modify `docker-compose.yml` and `docker-compose.dev.yml` to specify `user` using these variables and append `:z` to volume mounts to instruct Docker to relabel SELinux contexts.

**Tech Stack:** Docker, Docker Compose

## Global Constraints

- Run container processes as mapped host user (UID/GID) to prevent root-owned files on host.
- Use SELinux `:z` flag on all host volume mounts.
- Do not use deprecated `version` field in Docker Compose files.

---

### Task 1: Environment Variables Setup

**Files:**
- Modify: `.env.example`
- Modify: `.env`

**Interfaces:**
- Consumes: None
- Produces: `UID` and `GID` environment variables parsed by Docker Compose.

- [ ] **Step 1: Update .env.example**
  Modify [/.env.example](file:///home/thotsky/BrainVault/Projects/StashStats/.env.example) to add UID/GID defaults.
  ```env
  # Host User ID / Group ID for file permissions
  UID=1000
  GID=1000
  ```

- [ ] **Step 2: Update .env**
  Modify [/.env](file:///home/thotsky/BrainVault/Projects/StashStats/.env) to add UID/GID matching the host user.
  ```env
  # Host User ID / Group ID for file permissions
  UID=1000
  GID=1000
  ```

- [ ] **Step 3: Verify env vars**
  Run: `grep -E "^(UID|GID)=" .env`
  Expected output:
  ```
  UID=1000
  GID=1000
  ```

- [ ] **Step 4: Commit**
  Run:
  ```bash
  git add .env.example .env
  git commit -m "config: add UID and GID to environment configuration"
  ```

---

### Task 2: Update Main Docker Compose File

**Files:**
- Modify: `docker-compose.yml`

**Interfaces:**
- Consumes: `UID` and `GID` variables from Task 1.
- Produces: Web and Cache service configured to run as host user.

- [ ] **Step 1: Update docker-compose.yml**
  Modify [/docker-compose.yml](file:///home/thotsky/BrainVault/Projects/StashStats/docker-compose.yml) to add user configuration and `:z` mount flag.
  ```yaml
  services:
    web:
      build: .
      user: "${UID:-1000}:${GID:-1000}"
      command: gunicorn -b 0.0.0.0:8050 --workers 1 --threads 4 --timeout 120 --capture-output --log-level debug --access-logfile - --reload app:server
      ports:
        - "8050:8050"
      volumes:
        - .:/app:z
      environment:
        - API_USERNAME=${API_USERNAME}
        - API_KEY=${API_KEY}
        - RAVELRY_USERNAME=${RAVELRY_USERNAME}
        - REDIS_URL=redis://cache:6379/0
        - SQLITE_DB_PATH=/app/data/stash.db
      depends_on:
        cache:
          condition: service_started

    cache:
      image: redis:7-alpine
      user: "${UID:-1000}:${GID:-1000}"
      volumes:
        - redisdata:/data

  volumes:
    redisdata:
  ```

- [ ] **Step 2: Validate docker-compose.yml config**
  Run: `docker compose config`
  Expected: Outputs validated YAML configuration without errors or warnings about empty UID/GID.

- [ ] **Step 3: Commit**
  Run:
  ```bash
  git add docker-compose.yml
  git commit -m "deploy: update docker-compose user mapping and SELinux volume flags"
  ```

---

### Task 3: Update Dev Docker Compose Override

**Files:**
- Modify: `docker-compose.dev.yml`

**Interfaces:**
- Consumes: `UID` and `GID` variables from Task 1.
- Produces: Dev service override using the correct user and SELinux permissions.

- [ ] **Step 1: Update docker-compose.dev.yml**
  Modify [/docker-compose.dev.yml](file:///home/thotsky/BrainVault/Projects/StashStats/docker-compose.dev.yml) to remove `version` and update the `web` service user and volumes.
  ```yaml
  services:
    web:
      user: "${UID:-1000}:${GID:-1000}"
      volumes:
        - .:/app:z
      command: python app.py
      environment:
        - DEBUG=True
        - DEV_LOGGING=1
  ```

- [ ] **Step 2: Validate combined configuration**
  Run: `docker compose -f docker-compose.yml -f docker-compose.dev.yml config`
  Expected: Output contains the combined config with user mapping, `:z` mount flags, and python command without warnings.

- [ ] **Step 3: Commit**
  Run:
  ```bash
  git add docker-compose.dev.yml
  git commit -m "deploy: update docker-compose.dev.yml to match host user and SELinux specs"
  ```
