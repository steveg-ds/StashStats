import subprocess
import time
import os
import pytest
from unittest.mock import patch, MagicMock
from playwright.sync_api import sync_playwright
import sys

# Set default env vars for tests to pass Pydantic settings checks
os.environ.setdefault("API_USERNAME", "test_user")
os.environ.setdefault("API_KEY", "test_key")
os.environ.setdefault("RAVELRY_USERNAME", "test_user")

pytestmark = pytest.mark.skip(reason="Legacy E2E file superceded by tests/e2e/ Playwright suite")

# Mock DBManager & Redis globally in test runner
class MockDBManager:
    _history = {}
    _orig = {}
    _pending_dates = {}
    _next_id = 1
    _id_to_event = {}

    @classmethod
    def get_pool(cls):
        return MagicMock()

    @classmethod
    def get_original_values(cls, stash_id):
        return cls._orig.get(stash_id)

    @classmethod
    def get_bulk_original_values(cls, stash_ids):
        return {str(sid): cls._orig.get(str(sid)) for sid in stash_ids if str(sid) in cls._orig}

    @classmethod
    def save_original_values(cls, stash_id, yards, meters, skeins, grams):
        cls._orig[stash_id] = {"yards": yards, "meters": meters, "skeins": skeins, "grams": grams}

    @classmethod
    def get_stash_history(cls, stash_id):
        return cls._history.get(str(stash_id), [])

    @classmethod
    def get_bulk_stash_history(cls, stash_ids):
        return {str(sid): cls._history.get(str(sid), []) for sid in stash_ids}

    @classmethod
    def save_history_event(cls, stash_id, event_date, yards, meters, skeins, grams):
        event_id = cls._next_id
        cls._next_id += 1
        event = {
            "id": event_id,
            "stash_id": str(stash_id),
            "date": event_date,
            "yards": yards,
            "meters": meters,
            "skeins": skeins,
            "grams": grams
        }
        cls._history.setdefault(str(stash_id), []).append(event)
        cls._id_to_event[event_id] = event

    @classmethod
    def get_history_event(cls, event_id):
        return cls._id_to_event.get(event_id)

    @classmethod
    def delete_history_event(cls, event_id):
        event = cls._id_to_event.get(event_id)
        if event:
            stash_id = event["stash_id"]
            if stash_id in cls._history:
                cls._history[stash_id] = [e for e in cls._history[stash_id] if e["id"] != event_id]
            cls._id_to_event.pop(event_id, None)
            return True
        return False

    @classmethod
    def set_pending_usage_date(cls, stash_id, usage_date):
        cls._pending_dates[str(stash_id)] = usage_date

    @classmethod
    def pop_pending_usage_date(cls, stash_id):
        return cls._pending_dates.pop(str(stash_id), None)

    @classmethod
    def delete_stash_data(cls, stash_id):
        cls._orig.pop(str(stash_id), None)
        events = cls._history.pop(str(stash_id), None) or []
        for e in events:
            cls._id_to_event.pop(e["id"], None)

    @classmethod
    def run_migrations(cls):
        pass

    @classmethod
    def create_temperature_project(cls, name, location, lat, lon, start_date, end_date, temp_metric="mean", units="F", ravelry_project_id=None):
        return 1

    @classmethod
    def mark_dirty(cls, stash_id):
        pass

    @classmethod
    def get_dirty_stash_ids(cls):
        return []

    @classmethod
    def get_sync_state(cls, stash_id):
        return None

    @classmethod
    def mark_synced(cls, stash_id):
        pass

    @classmethod
    def get_unsynced_count(cls):
        return 0
        cls._pending_dates.pop(str(stash_id), None)

# Legacy test_e2e.py is skipped via pytestmark.

# Mock redis module
sys.modules['redis'] = MagicMock()

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
    from unittest.mock import patch, MagicMock

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
        elif "current_user.json" in url:
            mock_resp.json.return_value = {"user": {"username": "test_user"}}
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
            browser = p.chromium.launch(headless=True, slow_mo=100)
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
            
            # Wait for search results container to populate with card items
            page.wait_for_selector(".card")
            
            # Verify result item exists
            card_headers = page.locator(".card-header button")
            assert card_headers.count() > 0
            
            # Click the first card header to expand it
            card_headers.first.click()
            
            # Verify form elements are visible inside the expanded panel
            first_item = page.locator(".card").first
            first_item.locator("input[id*='stash-skeins']").wait_for(state="visible")
            
            # Fill the stash form
            first_item.locator("input[id*='stash-skeins']").fill("3.5")
            first_item.locator("input[id*='stash-dyelot']").fill("Batch A")
            first_item.locator("input[id*='stash-location']").fill("Living Room Box")
            first_item.locator("input[id*='stash-notes']").fill("Purchased during sale")
            
            # Click add yarn to stash button
            first_item.locator("button[id*='stash-submit-btn']").click()
            
            # Wait for the status message to appear and assert it
            status_msg = first_item.locator("div[id*='stash-status-msg']")
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
        if "stash/unified/list.json" in url:
            mock_resp.json.return_value = {
                "unified_stash": [
                    {
                        "stash": {
                            "id": 101,
                            "created_at": "2026/05/01 12:00:00 -0400",
                            "updated_at": "2026/05/01 12:00:00 -0400",
                            "yarn": {"yardage": 100},
                            "packs": [{"skeins": 2}]
                        }
                    },
                    {
                        "stash": {
                            "id": 102,
                            "created_at": "2026/05/15 12:00:00 -0400",
                            "updated_at": "2026/05/15 12:00:00 -0400",
                            "yarn": {"yardage": 150},
                            "packs": [{"skeins": 4}]
                        }
                    },
                    {
                        "stash": {
                            "id": 103,
                            "created_at": "2026/05/05 12:00:00 -0400",
                            "updated_at": "2026/05/20 12:00:00 -0400",
                            "yarn": {"yardage": 50},
                            "packs": [{"skeins": 3}]
                        }
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
        elif "current_user.json" in url:
            mock_resp.json.return_value = {"user": {"username": "test_user"}}
            return mock_resp
        return original_get(url, *args, **kwargs)

    with patch("requests.get", side_effect=mock_get):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=100)
            page = browser.new_page()
            
            page.goto(dash_thread_server)
            page.wait_for_load_state("networkidle")
            
            # Click analytics tab
            page.click("text=Stash Analytics")
            
            try:
                # Wait for Plotly Graph wrapper to be rendered
                page.wait_for_selector("text=Cumulative Stashed Yardage Over Time", timeout=5000)
            except Exception as e:
                print("\nTIMEOUT ERROR - PRINTING HTML CONTENT OF ANALYTICS CONTENT AREA:")
                print(page.locator("#analytics-content-area").inner_html())
                raise e
            
            # Check title elements
            graph_title = page.locator(".gtitle")
            assert graph_title.count() > 0

            # Toggle moving average checkbox
            page.check("#analytics-moving-average-checkbox")

            # Wait for updated graph title
            page.wait_for_selector("text=Cumulative Stashed Yardage Over Time (30-Day Moving Average)", timeout=5000)
            
            browser.close()


def test_new_tabs_flow(dash_thread_server):
    from unittest.mock import patch, MagicMock
    import requests
    
    original_get = requests.get
    original_post = requests.post
    original_delete = requests.delete
    
    def mock_get(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "stash/unified/list.json" in url:
            mock_resp.json.return_value = {
                "unified_stash": [
                    {
                        "stash": {
                            "id": 101,
                            "name": "Super Yarn",
                            "created_at": "2026/05/01 12:00:00 -0400",
                            "updated_at": "2026/05/01 12:00:00 -0400",
                            "yarn": {"yarn_company_name": "Co", "yardage": 100},
                            "packs": [{"skeins": 2}]
                        }
                    }
                ]
            }
            return mock_resp
        elif "projects/list.json" in url:
            mock_resp.json.return_value = {
                "projects": [
                    {
                        "id": 201,
                        "name": "Cozy Scarf",
                        "status_name": "In progress",
                        "craft_name": "Knitting",
                        "progress": 50,
                        "started": "2026/06/01",
                        "notes": "Using new alpaca yarn."
                    }
                ]
            }
            return mock_resp
        elif "queue/list.json" in url:
            mock_resp.json.return_value = {
                "queued_projects": [
                    {
                        "id": 301,
                        "name": "Warm Mittens",
                        "sort_order": 1,
                        "pattern_name": "Easy Mitts",
                        "yarn_name": "Wooly",
                        "skeins": 2,
                        "notes": "Gift for mom."
                    },
                    {
                        "id": 302,
                        "name": "Winter Hat",
                        "sort_order": 2,
                        "pattern_name": "Slouchy Beanie",
                        "yarn_name": "Soft Wool",
                        "skeins": 1
                    }
                ]
            }
            return mock_resp
        elif "needles/list.json" in url:
            mock_resp.json.return_value = {
                "needle_records": [
                    {
                        "id": 401,
                        "comment": "Circular needles",
                        "needle_size": {"us": "8", "metric": 5.0},
                        "needle_type": {"name": "Circular", "length": 24.0}
                    },
                    {
                        "id": 402,
                        "comment": "Crochet hook",
                        "needle_size": {"hook": "H", "metric": 5.0},
                        "needle_type": {"name": "Crochet Hook", "length": 6.0}
                    }
                ]
            }
            return mock_resp
        elif "current_user.json" in url:
            mock_resp.json.return_value = {"user": {"username": "test_user"}}
            return mock_resp
        return original_get(url, *args, **kwargs)

    def mock_post(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "reposition.json" in url:
            mock_resp.json.return_value = {"success": True}
            return mock_resp
        return original_post(url, *args, **kwargs)

    def mock_delete(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "queue/" in url:
            mock_resp.json.return_value = {"success": True}
            return mock_resp
        return original_delete(url, *args, **kwargs)

    with patch("requests.get", side_effect=mock_get), \
         patch("requests.post", side_effect=mock_post), \
         patch("requests.delete", side_effect=mock_delete):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=100)
            page = browser.new_page()
            
            page.goto(dash_thread_server)
            page.wait_for_load_state("networkidle")
            
            # 1. Verify Projects tab
            page.click("text=Projects")
            page.wait_for_selector("#projects-list-container")
            assert "Cozy Scarf" in page.content()
            
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


def test_animated_analytics():
    from stashies.model import Model
    m = Model()
    stash_list = [
        {
            "id": 201,
            "created_at": "2026/05/01 12:00:00 -0400",
            "updated_at": "2026/05/01 12:00:00 -0400",
            "yarn": {
                "yardage": 100,
                "grams": 50,
                "yarn_weight_name": "Worsted"
            },
            "packs": [{"skeins": 2}]
        },
        {
            "id": 202,
            "created_at": "2026/05/15 12:00:00 -0400",
            "updated_at": "2026/05/15 12:00:00 -0400",
            "yarn": {
                "yardage": 150,
                "grams": 100,
                "yarn_weight_name": "DK"
            },
            "packs": [{"skeins": 4}]
        }
    ]
    df = m.get_animated_analytics_dataframe(stash_list, {})
    assert not df.empty
    assert "cumulative_yards" in df.columns
    assert "cumulative_grams" in df.columns
    assert "frame_date" in df.columns
    assert "size_skeins" in df.columns
    
    categories = df["category"].unique()
    assert "Worsted" in categories
    assert "DK" in categories


def test_stash_pagination_and_sorting(dash_thread_server):
    import requests
    from unittest.mock import patch, MagicMock
    from playwright.sync_api import sync_playwright

    original_get = requests.get

    def mock_get(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "stash/unified/list.json" in url:
            # Return 12 stashes to trigger pagination (since page size is 10)
            unified_stash = []
            for i in range(12):
                unified_stash.append({
                    "stash": {
                        "id": 100 + i,
                        "name": f"Yarn {chr(65 + i)}", # Yarn A, Yarn B...
                        "created_at": f"2026/05/{10 + i:02d} 12:00:00 -0400",
                        "updated_at": f"2026/05/{10 + i:02d} 12:00:00 -0400",
                        "yarn": {"yarn_company_name": f"Brand {chr(90 - i)}", "yardage": 100}, # Brand Z, Brand Y...
                        "packs": [{"skeins": float(i + 1)}] # 1.0 to 12.0 skeins
                    }
                })
            mock_resp.json.return_value = {"unified_stash": unified_stash}
            return mock_resp
        elif "current_user.json" in url:
            mock_resp.json.return_value = {"user": {"username": "test_user"}}
            return mock_resp
        elif "stash/" in url and url.endswith(".json"):
            import re
            m = re.search(r"stash/(\d+)\.json", url)
            if m:
                stash_id = int(m.group(1))
                i = stash_id - 100
                if 0 <= i < 12:
                    mock_resp.json.return_value = {
                        "stash": {
                            "id": stash_id,
                            "updated_at": f"2026/05/{10 + i:02d} 12:00:00 -0400",
                            "packs": [{"skeins": float(i + 1), "total_yards": 100.0 * (i + 1)}]
                        }
                    }
                    return mock_resp
        return original_get(url, *args, **kwargs)

    with patch("requests.get", side_effect=mock_get):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=100)
            page = browser.new_page()
            page.goto(dash_thread_server)
            page.wait_for_load_state("networkidle")

            # Go to Personal Stash
            page.click("text=Personal Stash")
            page.wait_for_selector("#stash-list-container")

            # Default sort is brand_asc.
            # Verify first page has 10 items.
            accordions = page.locator("#stash-list-container .card")
            assert accordions.count() == 10

            # Verify pagination component exists and shows page 2 active indicator when clicked
            pagination_items = page.locator(".page-link")
            assert pagination_items.count() > 0

            # Go to page 2
            page.locator(".page-link").get_by_text("2", exact=True).click()
            page.wait_for_timeout(500) # Wait for animation/render
            assert page.locator("#stash-list-container .card").count() == 2

            # Reset to page 1 by sorting
            page.select_option("#stash-sort-by", "qty_desc")
            page.wait_for_timeout(500)
            # Quantity desc means Yarn 12 (Yarn L) is first
            assert page.locator("#stash-list-container .card").count() == 10

            browser.close()


def test_stash_edit_modal_flow_thread(dash_thread_server):
    import requests
    from unittest.mock import patch, MagicMock
    from playwright.sync_api import sync_playwright

    original_get = requests.get
    original_post = requests.post

    captured_posts = []

    def mock_get(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "stash/unified/list.json" in url:
            mock_resp.json.return_value = {
                "unified_stash": [
                    {
                        "stash": {
                            "id": 101,
                            "name": "Super Wool",
                            "created_at": "2026/05/01 12:00:00 -0400",
                            "updated_at": "2026/05/01 12:00:00 -0400",
                            "yarn": {
                                "id": 123,
                                "name": "Super Wool",
                                "yarn_company_name": "Cave Company",
                                "discontinued": False,
                                "grams": 100,
                                "yardage": 220,
                                "machine_washable": True,
                                "photos": [{"medium_url": "https://placehold.co/150"}]
                            },
                            "colorway_name": "Cave Red",
                            "dye_lot": "Batch A",
                            "location": "Living Room Box",
                            "notes": "Purchased during sale",
                            "packs": [{"skeins": 2.0}]
                        }
                    }
                ]
            }
            return mock_resp
        elif "stash/101.json" in url:
            mock_resp.json.return_value = {
                "stash": {
                    "id": 101,
                    "updated_at": "2026/05/01 12:00:00 -0400",
                    "packs": [{"skeins": 2.0, "total_yards": 440.0}]
                }
            }
            return mock_resp
        elif "current_user.json" in url:
            mock_resp.json.return_value = {"user": {"username": "test_user"}}
            return mock_resp
        return original_get(url, *args, **kwargs)

    def mock_post(url, *args, **kwargs):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        if "stash/101.json" in url:
            data = kwargs.get("json")
            captured_posts.append(data)
            mock_resp.json.return_value = {
                "stash": {
                    "id": 101,
                    "updated_at": "2026/05/02 12:00:00 -0400",
                    "packs": [{"skeins": 2.0, "total_yards": 440.0}]
                }
            }
            return mock_resp
        return original_post(url, *args, **kwargs)

    with patch("requests.get", side_effect=mock_get), patch("requests.post", side_effect=mock_post):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, slow_mo=100)
            page = browser.new_page()
            page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))
            page.on("pageerror", lambda err: print(f"BROWSER PAGEERROR: {err}"))
            page.goto(dash_thread_server)
            page.wait_for_load_state("networkidle")

            page.click("text=Personal Stash")
            page.wait_for_selector("#stash-list-container")

            assert "Super Wool" in page.content()

            # Click the collapse header to expand and show colorway rows
            page.click("[id*='yarn-collapse-btn']")

            # Click the edit button
            page.click("button[id*='stash-edit-btn'][id*='101']")

            # Wait for edit modal to open
            page.wait_for_selector("#edit-stash-modal", state="visible")

            # Check initial values in inputs
            assert page.locator("#edit-stash-colorway").input_value() == "Cave Red"
            assert page.locator("#edit-stash-dyelot").input_value() == "Batch A"
            assert page.locator("#edit-stash-location").input_value() == "Living Room Box"
            assert page.locator("#edit-stash-notes").input_value() == "Purchased during sale"

            # Modify some fields
            page.fill("#edit-stash-colorway", "New Cave Red")
            page.fill("#edit-stash-dyelot", "Batch B")
            page.fill("#edit-stash-location", "New Shelf")
            page.fill("#edit-stash-notes", "Used some for a hat")

            # Click save changes
            page.click("#edit-stash-save-btn")

            # Wait for edit modal to close
            page.wait_for_selector("#edit-stash-modal", state="hidden")

            # Verify POST was executed with correct payload
            assert len(captured_posts) > 0
            last_post = captured_posts[-1]
            assert last_post["location"] == "New Shelf"
            assert last_post["notes"] == "Used some for a hat"
            assert last_post.get("pack") is not None
            assert last_post["pack"].get("colorway") == "New Cave Red"
            assert last_post["pack"].get("dye_lot") == "Batch B"

            browser.close()


def test_delete_stash_flow():
    import stashies.app_controller
    from unittest.mock import patch, MagicMock
    
    with patch("app.CONTROLLER.handle_delete_stash") as mock_delete:
        mock_delete.return_value = ("Entry deleted successfully.", False)
        
        from app import handle_delete_confirm_submit
        
        res_msg, is_open, new_trigger = handle_delete_confirm_submit(
            submit_n_clicks=1,
            stash_id={"id": 123, "name": "Yarn A", "type": "yarn"},
            trigger_data=0
        )
        assert res_msg == "Entry deleted successfully."
        assert is_open is False
        assert new_trigger == 1
        mock_delete.assert_called_once_with(123, "yarn")


def test_log_usage_updates_analytics():
    import requests
    from unittest.mock import patch, MagicMock
    from stashies.model import Model
    from stashies.db import DBManager
    
    DBManager.delete_stash_data("101")
    
    model = Model()
    model.get_redis = MagicMock(return_value=None)
    model.REQ = MagicMock()
    
    model.REQ.get_request.side_effect = [
        # First fetch
        {
            "unified_stash": [
                {
                    "stash": {
                        "id": 101,
                        "created_at": "2026/05/01 12:00:00 -0400",
                        "updated_at": "2026/05/01 12:00:00 -0400",
                        "yarn": {"id": 123, "name": "Super Wool", "yardage": 220, "grams": 100},
                        "packs": [{"skeins": 2.0}]
                    }
                }
            ]
        },
        {
            "stash": {
                "id": 101,
                "created_at": "2026/05/01 12:00:00 -0400",
                "updated_at": "2026/05/01 12:00:00 -0400",
                "yarn": {"id": 123, "name": "Super Wool", "yardage": 220, "grams": 100},
                "packs": [{"skeins": 2.0}]
            }
        }
    ]
    
    stashes = model.get_stash_list()
    assert stashes is not None
    
    print("STASHES ARE:", stashes)
    
    orig = DBManager.get_bulk_original_values(["101"])
    assert "101" in orig
    assert orig["101"]["skeins"] == 2.0
    
    model.REQ.post_request.return_value = {
        "stash": {
            "id": 101,
            "updated_at": "2026/05/02 12:00:00 -0400",
            "packs": [{"skeins": 1.5}]
        }
    }
    
    DBManager.set_pending_usage_date("101", "2026-05-02")
    model.update_stash("101", {"pack": {"skeins": 1.5}})
    
    model.REQ.get_request.side_effect = [
        # Second fetch
        {
            "unified_stash": [
                {
                    "stash": {
                        "id": 101,
                        "created_at": "2026/05/01 12:00:00 -0400",
                        "updated_at": "2026/05/02 12:00:00 -0400",
                        "yarn": {"id": 123, "name": "Super Wool", "yardage": 220, "grams": 100},
                        "packs": [{"skeins": 1.5}]
                    }
                }
            ]
        },
        {
            "stash": {
                "id": 101,
                "created_at": "2026/05/01 12:00:00 -0400",
                "updated_at": "2026/05/02 12:00:00 -0400",
                "yarn": {"id": 123, "name": "Super Wool", "yardage": 220, "grams": 100},
                "packs": [{"skeins": 1.5}]
            }
        }
    ]
    
    stashes2 = model.get_stash_list()
    
    history = DBManager.get_stash_history("101")
    assert len(history) == 1
    assert history[0]["skeins"] == -0.5
    assert history[0]["date"] == "2026-05-02"
    
    df = model.get_analytics_dataframe(stashes2, {})
    assert not df.empty
    
    import pandas as pd
    row1 = df[df["date"] == pd.to_datetime("2026-05-01")]
    assert row1["cumulative_skeins"].iloc[0] == 2.0
    
    row2 = df[df["date"] == pd.to_datetime("2026-05-02")]
    assert row2["cumulative_skeins"].iloc[0] == 1.5
    
    DBManager.delete_stash_data("101")


def test_delete_usage_entry():
    from unittest.mock import patch, MagicMock
    from stashies.model import Model
    from stashies.db import DBManager

    DBManager.delete_stash_data("999")

    # Set original values so we have a baseline
    DBManager.save_original_values("999", yards=440.0, meters=400.0, skeins=2.0, grams=200.0)

    # Save a history event
    DBManager.save_history_event("999", "2026-05-02", yards=-110.0, meters=-100.0, skeins=-0.5, grams=-50.0)

    # Get the event ID
    history = DBManager.get_stash_history("999")
    assert len(history) == 1
    event_id = history[0]["id"]
    assert event_id is not None

    model = Model()
    model.get_redis = MagicMock(return_value=None)
    model.REQ = MagicMock()

    # Mock Ravelry API response for getting current stash detail
    # Assume current Ravelry skeins count is 1.5
    model.REQ.get_request.return_value = {
        "stash": {
            "id": 999,
            "packs": [{"skeins": 1.5}]
        }
    }

    # Mock Ravelry API response for update
    model.REQ.post_request.return_value = {
        "stash": {
            "id": 999,
            "packs": [{"skeins": 2.0}]
        }
    }

    # Call delete
    success = model.delete_stash_history_event(event_id)
    assert success is True

    # Verify event is deleted from SQLite
    assert DBManager.get_history_event(event_id) is None

    # Verify Ravelry update payload was sent with the reverted skeins (1.5 - (-0.5) = 2.0)
    model.REQ.post_request.assert_called_once()
    args, kwargs = model.REQ.post_request.call_args
    assert kwargs["data"]["pack"]["skeins"] == 2.0

    DBManager.delete_stash_data("999")



