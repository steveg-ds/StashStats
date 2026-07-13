# Technology Stack: StashStats

## Language
- **Python 3**: Core language for web app backend and the Ravelry API client package.

## Frontend Framework
- **Plotly Dash**: Interactive dashboard framework (`Dash`, `dcc`, `html`).
- **Dash Bootstrap Components (DBC)**: Styling theme framework (using Darkly theme).

## Database
- **PostgreSQL**: Relational database for storing user accounts, local stash cache, original purchase values, and usage history. Replaces SQLite to support concurrency and scaling.

## Cache & Queue
- **Redis**: In-memory data store for application caching, running as a service in Docker Compose.

## API Integration
- **Ravelry API**: Custom client package in `stashies/` wrapping Ravelry HTTP endpoints using standard HTTP requests/authentication.

## Infrastructure & Environment
- **Docker & Docker Compose**: Containerized multi-service stack (App, Redis, PostgreSQL).
- **Environment variables**: Local configuration and credential storage using `.env` (via python-dotenv).
