import subprocess
import time
import os
import pytest
from unittest.mock import patch, MagicMock
from playwright.sync_api import sync_playwright

import sys

@pytest.fixture(scope="module")
def dash_server():
    # Start the app server in a background subprocess
    # Dash will use the default port 8050
    proc = subprocess.Popen(
        [sys.executable, "app.py"],
        env={**os.environ, "API_USERNAME": "test_user", "API_KEY": "test_key", "USERNAME": "test_user"}
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


def test_stash_analytics_tab_thread(dash_thread_server):
    from unittest.mock import patch, MagicMock
    import requests
    
    original_get = requests.get
    
    def mock_get(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "stash/list.json" in url:
            mock_resp.json.return_value = {
                "stash": [
                    {
                        "id": 101,
                        "created_at": "2026/05/01 12:00:00 -0400",
                        "updated_at": "2026/05/01 12:00:00 -0400",
                        "yarn": {"yardage": 100},
                        "packs": [{"skeins": 2}]
                    },
                    {
                        "id": 102,
                        "created_at": "2026/05/15 12:00:00 -0400",
                        "updated_at": "2026/05/15 12:00:00 -0400",
                        "yarn": {"yardage": 150},
                        "packs": [{"skeins": 4}]
                    },
                    {
                        "id": 103,
                        "created_at": "2026/05/05 12:00:00 -0400",
                        "updated_at": "2026/05/20 12:00:00 -0400",
                        "yarn": {"yardage": 50},
                        "packs": [{"skeins": 3}]
                    }
                ]
            }
            return mock_resp
        elif "stash/101.json" in url:
            mock_resp.json.return_value = {
                "stash": {
                    "id": 101,
                    "updated_at": "2026/05/01 12:00:00 -0400",
                    "packs": [{"skeins": 2, "total_yards": 200}]
                }
            }
            return mock_resp
        elif "stash/102.json" in url:
            mock_resp.json.return_value = {
                "stash": {
                    "id": 102,
                    "updated_at": "2026/05/15 12:00:00 -0400",
                    "packs": [{"skeins": 4, "total_yards": 600, "project_id": 1001}]
                }
            }
            return mock_resp
        elif "stash/103.json" in url:
            mock_resp.json.return_value = {
                "stash": {
                    "id": 103,
                    "updated_at": "2026/05/20 12:00:00 -0400",
                    "stash_status": {"id": 2, "name": "Used up"},
                    "packs": [{"skeins": 3, "total_yards": 150}]
                }
            }
            return mock_resp
        elif "projects/list.json" in url:
            mock_resp.json.return_value = {
                "projects": [
                    {
                        "id": 1001,
                        "completed": "2026/05/10 12:00:00 -0400",
                        "created_at": "2026/05/10 12:00:00 -0400"
                    }
                ]
            }
            return mock_resp
        return original_get(url, *args, **kwargs)

    with patch("requests.get", side_effect=mock_get):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            page.goto(dash_thread_server)
            page.wait_for_load_state("networkidle")
            
            # Click analytics tab
            page.click("text=Stash Analytics")
            
            # Wait for Plotly Graph wrapper to be rendered
            page.wait_for_selector(".js-plotly-plot")
            
            # Check title elements
            graph_title = page.locator(".gtitle")
            assert graph_title.count() > 0
            
            browser.close()


def test_model_stash_history_and_deltas():
    from stashies.model import _get_primary_totals
    yarn_info = {"yardage": 200, "grams": 100}
    
    # 1. No packs fallback
    res1 = _get_primary_totals([], yarn_info)
    assert res1["yards"] == 200
    assert res1["skeins"] == 1.0
    
    # 2. Packs fallback with primary/child separation
    packs = [
        {"primary_pack_id": None, "skeins": 2.0, "total_yards": 400.0},
        {"primary_pack_id": 999, "skeins": 1.0, "total_yards": 200.0}
    ]
    res2 = _get_primary_totals(packs, yarn_info)
    assert res2["yards"] == 400.0
    assert res2["skeins"] == 2.0


def test_yarn_multiple_photos_validation():
    from stashies.dataclasses import Yarn
    raw_yarn = {
        "id": 123,
        "name": "Super Wool",
        "company": "Cave Company",
        "discontinued": False,
        "grams": 100,
        "yardage": 220,
        "machine_washable": True,
        "photos": [
            {"medium_url": "https://placehold.co/150"},
            {"medium_url": "https://placehold.co/250"}
        ]
    }
    y = Yarn(**raw_yarn)
    assert len(y.photos) == 2
    assert str(y.photos[0].medium) == "https://placehold.co/150"
    assert str(y.photos[1].medium) == "https://placehold.co/250"


def test_stash_card_carousel_rendering():
    from stashies.components.stash_card import StashCard
    import dash_bootstrap_components as dbc
    card = StashCard(container_id="test-card")
    s = {
        "id": 101,
        "name": "Super Wool",
        "yarn": {
            "yarn_company_name": "Cave Company",
            "photos": [
                {"medium_url": "https://placehold.co/150"},
                {"medium_url": "https://placehold.co/250"}
            ]
        },
        "stash_status": {"id": 1, "name": "In stash"}
    }
    totals = {"yards": 100, "meters": 91, "skeins": 1, "grams": 100}
    res = card.create_card(s, totals)
    
    # Store at res.children[0], Card at res.children[1]
    dbc_card = res.children[1]
    card_content = dbc_card.children[0]
    
    # Check that it rendered a Carousel because there are 2 photos
    # card_content is a Row because photos exist.
    # The first column in the Row should contain the carousel.
    img_col = card_content.children[0]
    carousel = img_col.children
    assert isinstance(carousel, dbc.Carousel)
    assert len(carousel.items) == 2
    assert carousel.items[0]["src"] == "https://placehold.co/150"





