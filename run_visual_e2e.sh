#!/usr/bin/env bash
# Script to run Playwright E2E tests in visible headed mode with slow-motion execution

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================="
echo " Starting StashStats Playwright Visual E2E Tests "
echo "================================================="
echo "Browser mode: HEADED (Visible)"
echo "Slow Motion:  800ms per action"
echo "-------------------------------------------------"

export HEADLESS=false
export SLOW_MO=800
export DATABASE_URL="postgresql://stashuser:stashpassword@localhost:5432/stashstats"
export PYTHONPATH="."
export CI=true

.venv/bin/pytest tests/e2e/ -s "$@"

echo "-------------------------------------------------"
echo " Visual E2E test execution complete! "
echo "================================================="
