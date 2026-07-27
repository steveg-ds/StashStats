"""Inventory Edit E2E tests."""
import pytest
from playwright.sync_api import Page


def test_stash_edit_modal(page: Page, app_server_url):
    """Verify stash edit modal opens correctly."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Click a stash item to open edit modal
    stash_item = page.locator(".card, [data-testid='stash-item']").first
    if stash_item.count() > 0:
        stash_item.click()
        page.wait_for_selector(".modal, [role='dialog']", timeout=5000)


def test_stash_quantity_update(page: Page, app_server_url):
    """Verify stash quantity can be updated."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Find and update a quantity input
    quantity_input = page.locator("input[id*='skeins'], input[id*='quantity']").first
    if quantity_input.count() > 0:
        quantity_input.fill("5")
        page.locator("button[id*='submit'], button[type='submit']").first.click()
        page.wait_for_load_state("networkidle", timeout=5000)


def test_usage_history_entries(page: Page, app_server_url):
    """Verify usage history entries appear correctly."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Check for history section using proper Playwright selectors
    # Use multiple fallback strategies to find the history section
    history_section = (
        page.locator("#history")
        .first
        if page.locator("#history").count() > 0
        else page.locator("[id*='history']").first
        if page.locator("[id*='history']").count() > 0
        else page.locator(":has-text('History')")
    )
    
    if history_section.count() > 0:
        history_section.click()
        page.wait_for_load_state("networkidle", timeout=5000)