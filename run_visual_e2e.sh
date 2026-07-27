#!/usr/bin/env bash
# Script to run Playwright E2E tests with a visible pop-up browser window

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================="
echo " Starting StashStats Visual E2E Pop-Up Browser   "
echo "================================================="
echo "HEADED:  true (Pop-up window enabled)"
echo "SLOW_MO: 800ms per action"
echo "-------------------------------------------------"

export HEADED=true
export SLOW_MO=800
export DATABASE_URL="postgresql://stashuser:stashpassword@localhost:5432/stashstats"
export PYTHONPATH="."
export CI=true

.venv/bin/pytest tests/e2e/ -s "$@"

echo "-------------------------------------------------"
echo " Visual E2E test execution complete! "
echo "================================================="
