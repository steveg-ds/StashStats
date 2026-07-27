# Specification: Docker Continuous Uptime & Remote Git Build Setup

## Overview
Update the Dockerfile and `docker-compose.yml` configuration so that the application stack builds from the remote GitHub repository and runs continuously with `restart: unless-stopped`.

## Functional Requirements
- **Dockerfile Updates**:
  - Support multi-stage Docker build that can clone/fetch code from the remote GitHub repository using build arguments (`REPO_URL` and `BRANCH`).
- **Docker Compose Configuration**:
  - Add `restart: unless-stopped` policy across `web`, `db`, and `cache` services.
  - Configure persistent volumes (`pgdata`, `redisdata`) to preserve database and cache data across container restarts.
  - Standardize environment configuration via `.env` and provide a complete `.env.example` template.
- **Production Readiness**:
  - Verify container healthchecks (`db` pg_isready) and dependency chains work seamlessly for 24/7 continuous operation.

## Acceptance Criteria
- `docker compose build` succeeds with remote Git build arguments.
- `docker compose up -d` starts all services in background with `restart: unless-stopped`.
- All automated unit tests and Docker stack healthchecks pass cleanly.
