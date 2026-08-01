import pytest
from playwright.sync_api import Page, expect

def test_sync_now_button_renders_on_stash_tab(page: Page, app_server_url):
    page.goto(app_server_url)
    page.wait_for_load_state("networkidle")
    page.click("text=Personal Stash")
    
    # Verify Sync Now button renders on Personal Stash page
    sync_btn = page.locator("#stash-sync-btn")
    expect(sync_btn).to_be_visible(timeout=5000)
    expect(sync_btn).to_contain_text("Sync Now")
    
    # Click Sync Now and verify status message updates
    sync_btn.click()
    status_msg = page.locator("#stash-sync-status-msg")
    expect(status_msg).to_be_visible(timeout=5000)
