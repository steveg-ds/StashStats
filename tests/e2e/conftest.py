"""Playwright E2E test configuration and fixtures."""
import os
import pytest
from playwright.sync_api import sync_playwright


@pytest.fixture(scope="module")
def browser_context():
    """Launch Chromium browser with configured context."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=100)
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        )
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="module")
def app_server_url():
    """Get the URL where the Dash app server runs."""
    return os.getenv('APP_SERVER_URL', 'http://localhost:8050')