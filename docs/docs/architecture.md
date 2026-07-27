# StashStats Architecture

## Tech Stack

- **Frontend**: Dash (Python framework)
- **Backend**: Flask API
- **Database**: PostgreSQL
- **Containerization**: Docker Compose
- **Deployment**: Local development with Docker, production with Tailscale

## Components

1. **StashStats Dashboard**: Real-time monitoring of stash items
2. **Ravelry API Integration**: API client for Ravelry data
3. **Database Layer**: ORM models for stash items, users, and analytics
4. **Analytics Engine**: Calculates metrics for stash usage and trends

## Docker Setup

- `docker-compose.yml`: Defines services (web, db, redis)
- `Dockerfile`: Builds the Dash application
- `docker-compose.override.yml`: Development overrides

## Dependencies

- Python 3.10+
- PostgreSQL 14+
- Redis 7+
- Docker >= 2.30.0
- Flask >= 2.0
- Dash >= 2.10.0

## Documentation Standards

- Use Markdown with GitHub Flavored Markdown (GFM)
- All code examples must be valid and tested
- Include version compatibility notes
- Maintain consistent heading structure