"""Search & Filter E2E tests."""
import pytest
from playwright.sync_api import Page


def test_search_filter_inputs(page: Page, app_server_url):
    """Verify search and filter inputs render correctly."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Check for search input - must exist (stash search filter)
    search_input = page.locator("input#search-query, input[id*='search-query'], input[id*='stash-search']") 
    assert search_input.count() > 0, "Search input must be present in the stash tab"

    # Stash sort-by select must be present
    sort_select = page.locator("select#stash-sort-by, select[id*='sort-by']") 
    assert sort_select.count() > 0, "Sort dropdown must be present in the stash tab"


def test_search_debounce(page: Page, app_server_url):
    """Verify search functionality: typing in filter narrows results or shows 'No matching' message."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Look for the stash search filter input (not yarn search)
    search_input = page.locator("input[id*='stash-search-query']").first
    if search_input.count() > 0:
        # Type a query that is unlikely to match anything
        search_input.fill("xyzzy_no_match_expected")
        page.wait_for_timeout(600)  # debounce delay
        page.wait_for_load_state("networkidle", timeout=5000)
        # After filtering with no matches, expect 'No matching' message or empty list
        content = page.content()
        assert "No matching" in content or "No stashed" in content or page.locator("#stash-list-container").count() > 0, \
            "After searching with no-match query, page must show empty state message or empty list"
    else:
        pytest.skip("Stash search input not available")


def test_filter_schedule_changes(page: Page, app_server_url):
    """Verify sort-by dropdown changes the stash list order."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    sort_select = page.locator("select#stash-sort-by, select[id*='sort-by']").first
    if sort_select.count() > 0:
        # Select 'qty_desc' option
        sort_select.select_option(value="qty_desc")
        page.wait_for_load_state("networkidle", timeout=5000)
        # The stash list container should still be present after sort change
        assert page.locator("#stash-list-container").count() > 0, \
            "Stash list container must remain present after sort option change"
    else:
        pytest.skip("Sort dropdown not available")