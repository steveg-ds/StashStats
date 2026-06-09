from playwright.sync_api import sync_playwright
import time
import sys

def test_live():
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            print("Navigating to app...")
            page.goto("http://localhost:8050")
            page.wait_for_load_state("networkidle")
            print(f"Title: {page.title()}")
            
            # Test 1: Search
            print("Testing search...")
            page.fill("#search-query", "wool")
            page.click("#search-button")
            page.wait_for_selector(".accordion-item", timeout=15000)
            print("Search results loaded.")
            
            # Test 2: Add to stash
            print("Testing stash add form...")
            accordion_headers = page.locator(".accordion-header")
            if accordion_headers.count() > 0:
                accordion_headers.first.click()
                page.wait_for_selector("input[id*='stash-skeins']", timeout=5000)
                page.fill("input[id*='stash-skeins']", "2")
                page.click("button[id*='stash-submit-btn']")
                status_msg = page.locator("div[id*='stash-status-msg']")
                page.wait_for_function("el => el.textContent !== ''", arg=status_msg.element_handle())
                print(f"Stash add response: {status_msg.inner_text()}")
            else:
                print("No search results to add.")

            # Test 3: Analytics
            print("Testing Analytics tab...")
            page.click("text=Stash Analytics")
            page.wait_for_selector(".js-plotly-plot", timeout=15000)
            print("Analytics graph rendered.")
            
            print("All core functionality tested successfully.")
        except Exception as e:
            print(f"Error during browser tests: {e}")
            sys.exit(1)
        finally:
            browser.close()

if __name__ == "__main__":
    test_live()
