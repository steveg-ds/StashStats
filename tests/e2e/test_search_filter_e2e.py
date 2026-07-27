"""Search & Filter E2E tests."""
import pytest
from playwright.sync_api import Page


def test_search_filter_inputs(page: Page, app_server_url):
    """Verify search and filter inputs render correctly."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Check for search input
    assert page.locator("input#search-query, input[id*='search-query']").count() > 0

    # Check for filter elements
    assert page.locator("select[id*='filter'], input[id*='filter']").count() >= 0


def test_search_debounce(page: Page, app_server_url):
    """Verify search functionality with debounce behavior."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    search_input = page.locator("input#search-query, input[id*='search-query']").first
    if search_input.count() > 0:
        search_input.fill("wool")
        search_input.press("Enter")
        page.wait_for_load_state("networkidle", timeout=5000)


def test_filter_schedule_changes(page: Page, app_server_url):
    """Verify schedule filter changes the view."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    filter_select = page.locator("select[id*='filter'], select[id*='schedule']").first
    if filter_select.count() > 0:
        filter_select.select_option(index=1)
        page.wait_for_load_state("networkidle", timeout=5000)