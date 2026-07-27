# Docker Compose Permissions and SELinux Design

## Goal

Redo Docker Compose setup to map the directory directly and avoid file permission issues on Fedora Linux (due to SELinux and default root user mapping).

## Design

### 1. Environment Configuration

Add `UID` and `GID` variables to `.env` and `.env.example` to map to the host user's UID/GID dynamically, with a safe fallback to `1000`.

### 2. Service User Configuration

Configure the `web` service in `docker-compose.yml` and `docker-compose.dev.yml` to run as the mapped user:
```yaml
user: "${UID:-1000}:${GID:-1000}"
```

### 3. Volume SELinux Context

Update volume mounts to include the `:z` suffix to allow shared SELinux labeling:
```yaml
volumes:
  - .:/app:z
```

### 4. Remove Deprecated Version Field

Remove `version` from Compose files as it is deprecated in modern Compose specifications.
