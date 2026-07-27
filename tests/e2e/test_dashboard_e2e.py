"""Dashboard E2E tests."""
import pytest
from playwright.sync_api import Page


def test_dashboard_layout(page: Page, app_server_url):
    """Verify dashboard layout renders correctly."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")
    
    # Check page title
    assert page.title() == "Stash Stats"
    
    # Wait for main tab to appear
    page.wait_for_selector("text=Personal Stash", timeout=10000)
    assert page.locator("text=Personal Stash").count() > 0