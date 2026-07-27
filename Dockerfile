# Stage 1: Build virtual environment with uv
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install git and compilation tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    git \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, deterministic builds
RUN pip install --no-cache-dir uv

ARG REPO_URL
ARG BRANCH=main

# Optionally clone from remote git repository if REPO_URL is supplied
RUN if [ -n "$REPO_URL" ]; then \
      git clone -b "${BRANCH}" "$REPO_URL" /app; \
    fi

COPY pyproject.toml README.md ./
COPY stashies/ ./stashies/

RUN uv venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN uv pip install -e .

# Stage 2: Minimal runtime image
FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY . .

EXPOSE 8050

CMD ["gunicorn", "-b", "0.0.0.0:8050", "--workers", "1", "--threads", "4", "--timeout", "120", "--capture-output", "--log-level", "debug", "--access-logfile", "-", "app:server"]
