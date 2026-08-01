import pytest
from playwright.sync_api import Page, expect

def test_temperature_blanket_tab_renders(page: Page, app_server_url: str):
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")
    
    # Click Temperature Blanket tab
    page.click("text=Temperature Blanket")
    
    # Check layout elements
    expect(page.locator("#temperature-blanket-container")).to_be_visible(timeout=5000)
    expect(page.locator("#open-temp-modal-btn")).to_be_visible(timeout=5000)
    expect(page.locator("#temp-grid-visualization")).to_be_visible(timeout=5000)
