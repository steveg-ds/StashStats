import subprocess
import time
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="module")
def dash_server():
    # Start the app server in a background subprocess
    # Dash will use the default port 8050
    proc = subprocess.Popen(
        [".venv/bin/python", "app.py"],
        env={"API_USERNAME": "test_user", "API_KEY": "test_key", "USERNAME": "test_user"}
    )
    # Wait for Dash app to launch
    time.sleep(3)
    yield "http://127.0.0.1:8050"
    # Kill the server process
    proc.terminate()
    proc.wait()

def test_stash_yarn_flow(dash_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Intercept and mock API requests
        def handle_route(route):
            url = route.request.url
            if "search.json" in url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body='{"yarns": [{"id": 123, "name": "Super Wool", "yarn_company_name": "Cave Company", "discontinued": false, "grams": 100, "yardage": 220, "machine_washable": true, "first_photo": {"medium_url": "https://placehold.co/150"}}], "paginator": {}}'
                )
            elif "123.json" in url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body='{"yarn": {"id": 123, "name": "Super Wool", "company_name": "Cave Company", "discontinued": false, "grams": 100, "yardage": 220, "machine_washable": true, "first_photo": {"medium_url": "https://placehold.co/150"}}, "colorways": [{"name": "Cave Red", "id": 1, "projects_count": 0, "stashes_count": 0}]}'
                )
            elif "create.json" in url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body='{"stash": {"id": 999}}'
                )
            else:
                route.continue_()

        # Route matching api.ravelry.com requests
        page.route("**/*api.ravelry.com*/**", handle_route)
        
        # Navigate to application
        page.goto(dash_server)
        
        # Verify title
        assert "Stash Stats" in page.title()
        
        # Find search input and type query
        page.fill("#search-query", "wool")
        
        # Click search button
        page.click("#search-button")
        
        # Wait for search results container to populate with accordion items
        page.wait_for_selector(".accordion-item")
        
        # Verify result item exists
        accordion_headers = page.locator(".accordion-header")
        assert accordion_headers.count() > 0
        
        # Click the first accordion header to expand it
        accordion_headers.first.click()
        
        # Verify form elements are visible inside the expanded panel
        page.wait_for_selector("input[id*='stash-skeins']")
        
        # Fill the stash form
        page.fill("input[id*='stash-skeins']", "3.5")
        page.fill("input[id*='stash-dyelot']", "Batch A")
        page.fill("input[id*='stash-location']", "Living Room Box")
        page.fill("input[id*='stash-notes']", "Purchased during sale")
        
        # Click add yarn to stash button
        page.click("button[id*='stash-submit-btn']")
        
        # Wait for the status message to appear and assert it
        status_msg = page.locator("div[id*='stash-status-msg']")
        page.wait_for_function("element => element.textContent !== ''", status_msg.element_handle())
        
        text = status_msg.inner_text()
        # Assert status output is received
        assert "Success" in text or "999" in text
        
        browser.close()

