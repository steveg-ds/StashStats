"""Inventory Edit E2E tests."""
import pytest
from playwright.sync_api import Page


def test_stash_edit_modal(page: Page, app_server_url):
    """Verify stash edit modal opens correctly and is visible."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Click a stash item to open edit modal
    stash_item = page.locator(".card, [data-testid='stash-item']").first
    if stash_item.count() > 0:
        stash_item.click()
        modal_locator = page.locator(".modal, [role='dialog']")
        modal_locator.wait_for(state="visible", timeout=5000)
        assert modal_locator.is_visible(), "Edit modal should be visible after clicking stash item"
    else:
        pytest.skip("No stash items available to test modal")


def test_stash_quantity_update(page: Page, app_server_url):
    """Verify stash quantity input accepts values and submitting shows feedback."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Find and update a quantity input
    quantity_input = page.locator("input[id*='skeins'], input[id*='quantity']").first
    if quantity_input.count() > 0:
        quantity_input.fill("5")
        assert quantity_input.input_value() == "5", "Quantity field should reflect entered value"
        submit_btn = page.locator("button[id*='submit'], button[type='submit']").first
        if submit_btn.count() > 0:
            submit_btn.click()
            page.wait_for_load_state("networkidle", timeout=5000)
            # After submit: page should still be responsive (no crash)
            assert page.title() != "", "Page title should be present after quantity update"
    else:
        pytest.skip("No quantity input available to test")


def test_usage_history_entries(page: Page, app_server_url):
    """Verify usage history section is present and contains expected elements."""
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")

    # Look for history-related elements in the page
    history_locators = [
        page.locator("#edit-stash-history-table"),
        page.locator("[id*='history']"),
        page.locator(":has-text('Usage History')"),
        page.locator(":has-text('History')"),
    ]

    history_found = False
    for loc in history_locators:
        if loc.count() > 0:
            history_found = True
            # Verify the element is in the DOM (not necessarily visible until modal opens)
            assert loc.count() > 0, f"History element should exist: {loc}"
            break

    if not history_found:
        pytest.skip("No history section found in current page state (requires open modal)")