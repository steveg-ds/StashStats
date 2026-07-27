# StashStats

## Setup

```bash
# Clone the repository
git clone https://github.com/BeigePowerRanger/stashstats.git
cd stashstats

# Start containers
docker compose up -d

# Initialize database (if needed)
docker compose exec db python manage.py setup

# Access app
open http://localhost:8000
```

## Requirements

- Docker >= 20.10
- Docker Compose >= 2.0
- Python 3.10+