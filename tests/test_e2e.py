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
    from unittest.mock import patch, MagicMock

    # Setup mocks for requests library inside the server context
    # Since requests calls happen in the Python server process, we can mock requests
    # within the test thread or simply mock them on the model/controller objects if they are loaded,
    # but the server is running in a subprocess. So let's mock it inside tests using standard patching or by
    # changing how the server is instantiated.
    # Actually, if we launch app.py in a subprocess, it won't share the main process's patches!
    # Instead of running as a subprocess, let's run the Dash app in a thread so it shares the python environment.
    pass

@pytest.fixture(scope="module")
def dash_thread_server():
    from threading import Thread
    import time
    from app import app
    
    # We run the Dash app in a background thread
    server_thread = Thread(target=lambda: app.run(host="127.0.0.1", port=8099, debug=False))
    server_thread.daemon = True
    server_thread.start()
    
    # Wait for Dash app to launch
    time.sleep(2)
    yield "http://127.0.0.1:8099"

def test_stash_yarn_flow_thread(dash_thread_server):
    from unittest.mock import patch
    import requests
    
    # We patch requests in the current process because the server runs in a thread here
    original_get = requests.get
    original_post = requests.post
    
    def mock_get(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "search.json" in url:
            mock_resp.json.return_value = {
                "yarns": [{
                    "id": 123, 
                    "name": "Super Wool", 
                    "yarn_company_name": "Cave Company", 
                    "discontinued": False, 
                    "grams": 100, 
                    "yardage": 220, 
                    "machine_washable": True, 
                    "first_photo": {"medium_url": "https://placehold.co/150"}
                }], 
                "paginator": {}
            }
            return mock_resp
        elif "123.json" in url:
            mock_resp.json.return_value = {
                "yarn": {
                    "id": 123, 
                    "name": "Super Wool", 
                    "company_name": "Cave Company", 
                    "discontinued": False, 
                    "grams": 100, 
                    "yardage": 220, 
                    "machine_washable": True, 
                    "first_photo": {"medium_url": "https://placehold.co/150"}
                }, 
                "colorways": [{"name": "Cave Red", "id": 1, "projects_count": 0, "stashes_count": 0}]
            }
            return mock_resp
        return original_get(url, *args, **kwargs)

    def mock_post(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "create.json" in url:
            mock_resp.json.return_value = {"stash": {"id": 999}}
            return mock_resp
        return original_post(url, *args, **kwargs)

    from unittest.mock import MagicMock
    with patch("requests.get", side_effect=mock_get), patch("requests.post", side_effect=mock_post):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # Navigate to application
            page.goto(dash_thread_server)
            page.wait_for_load_state("networkidle")
            
            # Verify title containing "Stash Stats"
            page.wait_for_function('document.title.includes("Stash Stats")')
            
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
            page.wait_for_function("el => el.textContent !== ''", arg=status_msg.element_handle())
            
            text = status_msg.inner_text()
            # Assert status output is received
            assert "Success" in text or "999" in text

            
            browser.close()


